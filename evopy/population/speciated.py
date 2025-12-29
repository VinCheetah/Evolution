"""
Defines the SpeciatedPopulation class, which implements NEAT-style speciation.
This population subdivides individuals into species based on genetic similarity.
"""

import random as rd
import numpy as np
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict

from evopy.population.base import BasePopulation
from evopy.individual.base import BaseIndividual
from evopy.individual.neural_network.neat import NEATIndividual


class Species:
    """
    Represents a species containing genetically similar individuals.
    
    Attributes:
        representative (BaseIndividual): The representative individual for this species
        members (List[BaseIndividual]): All individuals belonging to this species
        age (int): How many generations this species has existed
        last_improvement (int): Generation when this species last improved
        max_fitness_ever (float): Best fitness this species has ever achieved
        adjusted_fitness (float): Species fitness adjusted for sharing
    """
    
    def __init__(self, representative: BaseIndividual):
        self.representative: BaseIndividual = representative
        self.members: List[BaseIndividual] = [representative]
        self.age: int = 0
        self.last_improvement: int = 0
        self.max_fitness_ever: float = float('-inf')
        self.adjusted_fitness: float = 0.0
        self.stagnant: bool = False
        
    def add_member(self, individual: BaseIndividual) -> None:
        """Add an individual to this species."""
        self.members.append(individual)
        
    def clear_members(self) -> None:
        """Clear all members except the representative."""
        self.members = [self.representative]
        
    def get_average_fitness(self) -> float:
        """Calculate the average fitness of all members."""
        if not self.members:
            return 0.0
        valid_fitness = [ind.fitness for ind in self.members if not np.isnan(ind.fitness)]
        return float(np.mean(valid_fitness)) if valid_fitness else 0.0
        
    def get_best_fitness(self) -> float:
        """Get the best fitness in this species."""
        if not self.members:
            return float('-inf')
        valid_fitness = [ind.fitness for ind in self.members if not np.isnan(ind.fitness)]
        return max(valid_fitness) if valid_fitness else float('-inf')
        
    def update_age(self) -> None:
        """Increment species age."""
        self.age += 1
        
    def check_improvement(self, generation: int) -> None:
        """Check if species improved and update tracking variables."""
        current_best = self.get_best_fitness()
        if current_best > self.max_fitness_ever:
            self.max_fitness_ever = current_best
            self.last_improvement = generation
            self.stagnant = False
        
    def select_new_representative(self) -> None:
        """Select a new representative from currentEliteSelector members."""
        if self.members:
            self.representative = rd.choice(self.members)


class SpeciatedPopulation(BasePopulation):
    """
    Population that implements NEAT-style speciation based on genetic distance.
    
    Additional Parameters:
        * compatibility_threshold (float): Threshold for determining species membership
            Default: 3.0
        * c1 (float): Coefficient for excess genes in compatibility distance
            Default: 1.0
        * c2 (float): Coefficient for disjoint genes in compatibility distance
            Default: 1.0
        * c3 (float): Coefficient for weight differences in compatibility distance
            Default: 0.4
        * compatibility_modifier (float): Dynamic threshold adjustment rate
            Default: 0.3
        * target_species (int): Target number of species to maintain
            Default: 10
        * max_stagnation (int): Generations before removing stagnant species
            Default: 15
        * min_species_size (int): Minimum size for a species to survive
            Default: 2
        * elitism_threshold (int): Species size threshold for elitism
            Default: 5
    """
    
    component_name: str = "Population"
    component_type: str = "Speciated"
    
    def __init__(self, options, **kwargs):
        options.update(kwargs)
        super().__init__(options)
        
        # Speciation parameters
        self._compatibility_threshold: float = getattr(options, 'compatibility_threshold', 3.0)
        self._c1: float = getattr(options, 'c1', 1.0)  # Excess genes coefficient
        self._c2: float = getattr(options, 'c2', 1.0)  # Disjoint genes coefficient  
        self._c3: float = getattr(options, 'c3', 0.4)  # Weight difference coefficient
        self._compatibility_modifier: float = getattr(options, 'compatibility_modifier', 0.3)
        self._target_species: int = getattr(options, 'target_species', 10)
        self._max_stagnation: int = getattr(options, 'max_stagnation', 15)
        self._min_species_size: int = getattr(options, 'min_species_size', 2)
        self._elitism_threshold: int = getattr(options, 'elitism_threshold', 5)
        
        # Species tracking
        self._species: List[Species] = []
        self._generation: int = 0
        self._species_id_counter: int = 0
        
        # Initialize speciation
        self._speciate_population()
    
    def update(self, selection):
        """Update population and re-speciate."""
        super().update(selection)
        self._generation += 1
        self._speciate_population()
        self._adjust_compatibility_threshold()
        self._remove_stagnant_species()
        self.log("info", f"Generation {self._generation}: {len(self._species)} species")
    
    def _calculate_genetic_distance(self, genome1: BaseIndividual, genome2: BaseIndividual) -> float:
        """
        Calculate the genetic distance between two NEAT genomes.
        
        Distance formula: δ = (c1*E/N) + (c2*D/N) + c3*W̄
        Where:
        - E = number of excess genes
        - D = number of disjoint genes  
        - N = number of genes in the larger genome
        - W̄ = average weight difference of matching genes
        """
        # Verify both genomes are NEAT individuals
        if not (isinstance(genome1, NEATIndividual) and isinstance(genome2, NEATIndividual)):
            raise TypeError("SpeciatedPopulation requires NEATIndividual instances")
            
        # Get connection genes from both genomes
        connections1 = {conn.id: conn for conn in genome1.connections}
        connections2 = {conn.id: conn for conn in genome2.connections}
        
        # Find all gene IDs and determine ranges
        all_ids1 = set(connections1.keys())
        all_ids2 = set(connections2.keys())
        all_ids = all_ids1.union(all_ids2)
        
        if not all_ids:
            return 0.0
            
        # Determine the range of gene IDs for each genome
        max_id1 = max(all_ids1) if all_ids1 else -1
        max_id2 = max(all_ids2) if all_ids2 else -1
        min_common_max = min(max_id1, max_id2)
        
        # Count excess, disjoint, and matching genes
        excess_count = 0
        disjoint_count = 0
        matching_genes = []
        
        for gene_id in all_ids:
            in_genome1 = gene_id in connections1
            in_genome2 = gene_id in connections2
            
            if in_genome1 and in_genome2:
                # Matching gene - store weight difference
                weight_diff = abs(connections1[gene_id].weight - connections2[gene_id].weight)
                matching_genes.append(weight_diff)
            elif gene_id > min_common_max:
                # Excess gene (beyond the range of the smaller genome)
                excess_count += 1
            else:
                # Disjoint gene (gap in the middle)
                disjoint_count += 1
        
        # Calculate average weight difference
        avg_weight_diff = np.mean(matching_genes) if matching_genes else 0.0
        
        # Normalize by genome size (number of genes in larger genome)
        N = max(len(all_ids1), len(all_ids2))
        N = max(N, 1)  # Avoid division by zero
        
        # Calculate compatibility distance
        distance = (self._c1 * excess_count / N + 
                   self._c2 * disjoint_count / N + 
                   self._c3 * avg_weight_diff)
        
        return float(distance)
    
    def _find_species_for_individual(self, individual: BaseIndividual) -> Optional[Species]:
        """Find the species that this individual belongs to, or None if no match."""
        for species in self._species:
            distance = self._calculate_genetic_distance(individual, species.representative)
            if distance < self._compatibility_threshold:
                return species
        return None
    
    def _speciate_population(self) -> None:
        """Assign all individuals to species based on genetic similarity."""
        # Clear existing species memberships but keep representatives
        for species in self._species:
            species.clear_members()
        
        # Remove empty species
        self._species = [s for s in self._species if s.representative in self._population]
        
        # Assign each individual to a species
        unassigned = []
        for individual in self._population:
            species = self._find_species_for_individual(individual)
            if species:
                species.add_member(individual)
            else:
                unassigned.append(individual)
        
        # Create new species for unassigned individuals
        for individual in unassigned:
            new_species = Species(individual)
            self._species.append(new_species)
        
        # Update species age and check for improvement
        for species in self._species[:]:  # Copy list since we might modify it
            species.update_age()
            species.check_improvement(self._generation)
            
        # Remove empty species
        self._species = [s for s in self._species if s.members]
        
        # Select new representatives for next generation
        for species in self._species:
            species.select_new_representative()
    
    def _adjust_compatibility_threshold(self) -> None:
        """Dynamically adjust compatibility threshold to maintain target species count."""
        current_species_count = len(self._species)
        
        if current_species_count < self._target_species:
            # Too few species - lower threshold to create more species
            self._compatibility_threshold -= self._compatibility_modifier
        elif current_species_count > self._target_species:
            # Too many species - raise threshold to merge species
            self._compatibility_threshold += self._compatibility_modifier
            
        # Keep threshold in reasonable bounds
        self._compatibility_threshold = max(0.1, min(10.0, self._compatibility_threshold))
    
    def _remove_stagnant_species(self) -> None:
        """Remove species that have been stagnant for too long."""
        species_to_remove = []
        
        for species in self._species:
            generations_stagnant = self._generation - species.last_improvement
            if (generations_stagnant >= self._max_stagnation and 
                len(species.members) < self._min_species_size):
                species_to_remove.append(species)
                
        # Remove stagnant species from population
        for species in species_to_remove:
            self._species.remove(species)
            # Remove individuals from this species from the population
            for individual in species.members:
                if individual in self._population:
                    self._population.remove(individual)
                    
        if species_to_remove:
            self.log("info", f"Removed {len(species_to_remove)} stagnant species")
    
    def get_species_info(self) -> Dict:
        """Get information about current species."""
        species_info = {
            'num_species': len(self._species),
            'compatibility_threshold': self._compatibility_threshold,
            'species_details': []
        }
        
        for i, species in enumerate(self._species):
            species_detail = {
                'id': i,
                'size': len(species.members),
                'age': species.age,
                'avg_fitness': species.get_average_fitness(),
                'best_fitness': species.get_best_fitness(),
                'stagnant_generations': self._generation - species.last_improvement,
                'adjusted_fitness': species.adjusted_fitness
            }
            species_info['species_details'].append(species_detail)
            
        return species_info
    
    def get_species_by_individual(self, individual: BaseIndividual) -> Optional[Species]:
        """Find which species an individual belongs to."""
        for species in self._species:
            if individual in species.members:
                return species
        return None
    
    def calculate_shared_fitness(self) -> None:
        """Calculate fitness sharing within species."""
        for species in self._species:
            if not species.members:
                continue
                
            # Calculate shared fitness for each member
            species_size = len(species.members)
            total_fitness = 0.0
            
            for individual in species.members:
                if not np.isnan(individual.fitness):
                    # Fitness sharing: divide by species size
                    shared_fitness = individual.fitness / species_size
                    total_fitness += shared_fitness
            
            species.adjusted_fitness = total_fitness / species_size if species_size > 0 else 0.0
    
    def get_species_representatives(self) -> List[BaseIndividual]:
        """Get all species representatives."""
        return [species.representative for species in self._species]
    
    def show_species_summary(self) -> str:
        """Show a summary of all species."""
        msg = f"\nSpecies Summary (Generation {self._generation}):\n"
        msg += f"Total species: {len(self._species)}\n"
        msg += f"Compatibility threshold: {self._compatibility_threshold:.3f}\n"
        msg += "-" * 60 + "\n"
        
        for i, species in enumerate(self._species):
            msg += f"Species {i}: {len(species.members)} members, "
            msg += f"age: {species.age}, "
            msg += f"best: {species.get_best_fitness():.3f}, "
            msg += f"avg: {species.get_average_fitness():.3f}\n"
            
        return msg
    
    def show(self):
        """Show the population with species information."""
        base_msg = super().show()
        species_msg = self.show_species_summary()
        return base_msg + species_msg