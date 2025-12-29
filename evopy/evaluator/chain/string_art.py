"""
StringArtEvaluator

Evaluator for string-art style pattern generation. Implements a composite
fitness combining global residual (MSE), structural similarity (SSIM),
gradient (Sobel) fidelity and aesthetic penalties for duplicate segments
and local density.

The evaluator expects an options object providing at least a target image
(`target_image`) as a numpy array or a callable `render_func` able to
render a chain into an image. If no `render_func` is provided the chain
itself is assumed to be an image-like numpy array.

Weights default to the values suggested in the specification.
"""

from collections import Counter
from typing import Callable, Optional, Sequence

import numpy as np
from scipy.signal import convolve2d

from evopy.evaluator.chain.base import ChainEvaluator
from evopy.evaluator.graphic import GraphicReprEvaluator


def _to_gray(img: np.ndarray) -> np.ndarray:
    """Convert image to grayscale float32 array in [0,1]."""
    img = np.asarray(img, dtype=np.float32)
    if img.ndim == 3:
        # assume RGB or RGBA
        if img.shape[2] == 4:
            img = img[..., :3]
        # luminosity method
        img = 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]
    # normalize if needed
    if img.max() > 1.0:
        img = img / 255.0
    return img


def _mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2))


def _sobel_magnitude(img: np.ndarray) -> np.ndarray:
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    ky = kx.T
    gx = convolve2d(img, kx, mode="same", boundary="symm")
    gy = convolve2d(img, ky, mode="same", boundary="symm")
    return np.hypot(gx, gy)


def _ssim_safe(a: np.ndarray, b: np.ndarray) -> float:
    """Try to compute SSIM with skimage; fallback to correlation-based proxy."""
    try:
        from skimage.metrics import structural_similarity as ssim

        val = ssim(a, b, data_range=1.0)
        # skimage may return negative values in some rare cases; clamp to [0,1]
        return float(np.clip(val, 0.0, 1.0))
    except Exception:
        # fallback: normalized Pearson correlation mapped to [0,1]
        fa = a.flatten()
        fb = b.flatten()
        if fa.size == 0:
            return 0.0
        # subtract mean
        fa -= fa.mean()
        fb -= fb.mean()
        denom = np.sqrt(np.sum(fa * fa) * np.sum(fb * fb))
        if denom <= 0:
            return 0.0
        corr = float(np.sum(fa * fb) / denom)
        return float(np.clip((corr + 1.0) / 2.0, 0.0, 1.0))


def _resize_with_fallback(img: np.ndarray, target_shape: Optional[Sequence[int]]) -> np.ndarray:
    """Resize using skimage when available, fall back to crop/pad."""
    if target_shape is None:
        return img
    target_shape = tuple(int(x) for x in target_shape)
    if img.shape == target_shape:
        return img
    try:
        from skimage.transform import resize as _resize

        resized = _resize(img, target_shape, preserve_range=True, anti_aliasing=True)
        return resized.astype(np.float32)
    except Exception:
        h, w = target_shape
        out = np.zeros((h, w), dtype=np.float32)
        th, tw = img.shape
        out[: min(h, th), : min(w, tw)] = img[: min(h, th), : min(w, tw)]
        return out


class StringArtEvaluator(ChainEvaluator, GraphicReprEvaluator):
    """Evaluator implementing the composite fitness for string-art.

    Options used (defaults provided):
        * target_image (np.ndarray): reference image (required unless provided at runtime)
        * render_func (Callable[[chain], np.ndarray] | None): function rendering a chain to an image. If None the chain is expected to be an image array.
        * image_size (tuple): expected size (height, width) of images; used to resize target/candidate if needed.
        * mse_weight: 0.5
        * ssim_weight: 0.3
        * grad_weight: 0.15
        * dup_weight: 0.03
        * dens_weight: 0.02
        * density_allowed: 0.20  # maximum allowed local stroke density before penalty
        * density_threshold: 1e-3  # pixel intensity threshold to consider "covered"
        * density_kernel: 11  # local neighborhood (odd size) for density estimation
    """

    component_type: str = "StringArt"

    def __init__(self, options, **kwargs):
        options.update(kwargs)
        ChainEvaluator.__init__(self, options)
        GraphicReprEvaluator.__init__(self, options)

        opt = self._options
        # attach defaults after evaluator init to keep options object consistent
        opt.mse_weight = getattr(opt, "mse_weight", 0.5)
        opt.ssim_weight = getattr(opt, "ssim_weight", 0.3)
        opt.grad_weight = getattr(opt, "grad_weight", 0.15)
        opt.dup_weight = getattr(opt, "dup_weight", 0.03)
        opt.dens_weight = getattr(opt, "dens_weight", 0.02)
        opt.density_allowed = getattr(opt, "density_allowed", 0.20)
        opt.density_threshold = getattr(opt, "density_threshold", 1e-3)
        opt.density_kernel = int(getattr(opt, "density_kernel", 11)) or 1
        if opt.density_kernel % 2 == 0:
            opt.density_kernel += 1
        opt.render_func = getattr(opt, "render_func", None)
        opt.target_image = getattr(opt, "target_image", None)
        opt.image_size = getattr(opt, "image_size", None)

        self._weights = {
            "mse": float(opt.mse_weight),
            "ssim": float(opt.ssim_weight),
            "grad": float(opt.grad_weight),
            "dup": float(opt.dup_weight),
            "dens": float(opt.dens_weight),
        }

        self._density_allowed = float(opt.density_allowed)
        self._density_threshold = float(opt.density_threshold)
        self._density_kernel = int(opt.density_kernel)
        self._render_func: Optional[Callable] = opt.render_func

        desired_shape = tuple(opt.image_size) if opt.image_size is not None else None
        self._image_shape: Optional[tuple[int, int]] = desired_shape

        self._target = self._prepare_target(opt.target_image)
        self._target_grad = _sobel_magnitude(self._target) if self._target is not None else None
        self._last_candidate_gray: Optional[np.ndarray] = None
        self._last_candidate_rgb: Optional[np.ndarray] = None
        self._last_metrics: dict[str, float] = {}

    def set_target_image(self, image: np.ndarray) -> None:
        """Update the reference image at runtime (useful for curriculum learning)."""
        self._target = self._prepare_target(image)
        self._target_grad = _sobel_magnitude(self._target) if self._target is not None else None

    def _prepare_target(self, target_image: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if target_image is None:
            return None
        gray = _to_gray(target_image)
        gray = _resize_with_fallback(gray, self._image_shape or gray.shape)
        gray = np.clip(gray.astype(np.float32), 0.0, 1.0)
        self._image_shape = gray.shape
        return gray

    def _render_candidate(self, chain) -> np.ndarray:
        if self._render_func is not None and callable(self._render_func):
            cand = self._render_func(chain)
        else:
            cand = np.asarray(chain)
        gray = _to_gray(cand)
        target_shape = self._image_shape or (self._target.shape if self._target is not None else gray.shape)
        gray = _resize_with_fallback(gray, target_shape)
        gray = np.clip(gray.astype(np.float32), 0.0, 1.0)
        self._image_shape = gray.shape
        self._last_candidate_gray = gray
        self._last_candidate_rgb = np.asarray(cand)
        return gray

    def _duplicates_penalty(self, chain) -> float:
        try:
            arr = np.asarray(chain)
            if arr.ndim != 1 or not np.issubdtype(arr.dtype, np.integer) or arr.size < 2:
                return 0.0
            start = arr[:-1]
            end = arr[1:]
            mask = start != end
            if not np.any(mask):
                return 0.0
            start = start[mask].astype(np.int64, copy=False)
            end = end[mask].astype(np.int64, copy=False)
            segs = np.stack((np.minimum(start, end), np.maximum(start, end)), axis=1)
            if segs.size == 0:
                return 0.0
            _, counts = np.unique(segs, axis=0, return_counts=True)
            duplicates = counts[counts > 1] - 1
            return float(duplicates.sum()) / max(1, segs.shape[0])
        except Exception:
            return 0.0

    def _density_penalty(self, img: np.ndarray) -> float:
        if img.size == 0:
            return 0.0
        mask = (img > self._density_threshold).astype(np.float32)
        kernel = np.ones((self._density_kernel, self._density_kernel), dtype=np.float32)
        kernel /= kernel.size
        local_density = convolve2d(mask, kernel, mode="same", boundary="symm")
        rho_actual = float(local_density.max())
        penalty = max(0.0, (rho_actual - self._density_allowed) / max(1e-8, self._density_allowed))
        return float(np.clip(penalty, 0.0, 1.0))

    def _evaluate_chain(self, chain) -> float:
        if self._target is None:
            raise ValueError("StringArtEvaluator requires a target_image to be set before evaluation")

        It = self._target
        Is = self._render_candidate(chain)

        mse_val = _mse(It, Is)
        fmse = 1.0 / (1.0 + mse_val)

        fssim = _ssim_safe(It, Is)

        gt = self._target_grad if self._target_grad is not None else _sobel_magnitude(It)
        gs = _sobel_magnitude(Is)
        grad_mse = _mse(gt, gs)
        fgrad = 1.0 / (1.0 + grad_mse)

        pdup = self._duplicates_penalty(chain)
        pdens = self._density_penalty(Is)

        fitness = (
            self._weights["mse"] * fmse
            + self._weights["ssim"] * fssim
            + self._weights["grad"] * fgrad
            - self._weights["dup"] * pdup
            - self._weights["dens"] * pdens
        )

        self._last_metrics = {
            "fmse": fmse,
            "fssim": fssim,
            "fgrad": fgrad,
            "pdup": pdup,
            "pdens": pdens,
            "fitness": fitness,
        }

        return float(fitness)

    # -- Graphic representation -------------------------------------------------

    def init_plot(self, ax) -> None:
        if self._image_shape is None and self._target is not None:
            self._image_shape = self._target.shape
        shape = self._image_shape or (32, 32)
        placeholder = np.zeros(shape, dtype=np.float32)
        axs = self.create_subplots(ax, (1, 3))
        titles = ("Target", "Candidate", "Abs diff")
        curve_map = {}
        for idx, subax in enumerate(axs.flatten()):
            img = subax.imshow(placeholder, cmap="gray", vmin=0.0, vmax=1.0)
            subax.set_title(titles[idx])
            subax.axis("off")
            key = ("target", "candidate", "diff")[idx]
            curve_map[key] = img
        self.set_curves(ax, curve_map)

    def plot(self, ax, individual) -> None:
        if self._target is None:
            return
        candidate = self._render_candidate(individual.get_chain())
        diff = np.abs(self._target - candidate)
        curves = self.get_curves(ax)
        curves["target"].set_data(self._target)
        curves["candidate"].set_data(candidate)
        curves["diff"].set_data(diff)

