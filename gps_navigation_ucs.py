import heapq
import time
import os
from collections import defaultdict

class PhilippineHighwayNavigatorUCS:
    def __init__(self):
        self.graph = {}  # adjacency list with costs
        self.locations = {}  # location names mapping
        self.start = None
        self.goal = None
        
    def add_location(self, location_id, name):
        """Add a Philippine location to the navigation system"""
        self.locations[location_id] = name
        if location_id not in self.graph:
            self.graph[location_id] = []
    
    def add_highway(self, from_loc, to_loc, distance_km, traffic_factor=1.0, toll_php=0, highway_name=""):
        """
        Add a bidirectional highway between two Philippine locations
        Cost = distance_km * traffic_factor + toll_php/10 (convert to consistent units)
        """
        # Convert toll from PHP to cost units (divide by 10 for scaling)
        total_cost = distance_km * traffic_factor + (toll_php / 10.0)
        
        # Add bidirectional edges
        if from_loc not in self.graph:
            self.graph[from_loc] = []
        if to_loc not in self.graph:
            self.graph[to_loc] = []
            
        self.graph[from_loc].append((to_loc, total_cost, distance_km, traffic_factor, toll_php, highway_name))
        self.graph[to_loc].append((from_loc, total_cost, distance_km, traffic_factor, toll_php, highway_name))
    
    def display_network(self, visited=None, current=None, path=None):
        """Display the current state of the Philippine highway network"""
        print("\n" + "="*80)
        print("🇵🇭 PHILIPPINE HIGHWAY NAVIGATOR - UNIFORM COST SEARCH 🇵🇭")
        print("="*80)
        print("Highway Network Status:")
        print("- Current: exploring this location")
        print("- Visited: already explored with optimal cost")
        print("- Path: final optimal route")
        print("-"*80)
        
        for loc_id, name in self.locations.items():
            status = ""
            if path and loc_id in [p[0] for p in path]:
                status = " [PATH] 🛣️"
            elif current and loc_id == current:
                status = " [CURRENT] 📍"
            elif visited and loc_id in visited:
                status = f" [VISITED: cost={visited[loc_id]:.1f}] ✅"
            
            print(f"{name} (ID: {loc_id}){status}")
            
            # Show highway connections
            if loc_id in self.graph:
                for neighbor, cost, distance, traffic, toll, highway in self.graph[loc_id]:
                    neighbor_name = self.locations.get(neighbor, f"ID-{neighbor}")
                    highway_info = f" via {highway}" if highway else ""
                    print(f"  → {neighbor_name}: cost={cost:.1f} ({distance:.0f}km, "
                          f"traffic={traffic:.1f}x, toll=₱{toll:.0f}){highway_info}")
        print("-"*80)
    
    def ucs_search(self, start, goal, show_steps=True, delay=1):
        """
        Uniform Cost Search implementation for Philippine highway navigation
        Returns: (path, total_cost, total_distance, total_toll) or (None, None, None, None)
        """
        self.start = start
        self.goal = goal
        
        if start not in self.graph or goal not in self.graph:
            print("Error: Start or Goal location not found in Philippine highway network!")
            return None, None, None, None
        
        start_name = self.locations.get(start, f"ID-{start}")
        goal_name = self.locations.get(goal, f"ID-{goal}")
        
        print(f"🚗 Starting navigation from {start_name} to {goal_name}")
        print("🏖️ Navigating through the beautiful Philippines! 🏔️")
        self.display_network()
        
        if show_steps:
            input("Press Enter to start UCS navigation...")
        
        # Priority queue: (cost, current_location, path_info)
        # path_info contains: [(location, cumulative_cost, cumulative_distance, cumulative_toll, highway_used)]
        priority_queue = [(0, start, [(start, 0, 0, 0, "Starting Point")])]
        visited = {}  # location -> best_cost_so_far
        step = 0
        
        while priority_queue:
            step += 1
            current_cost, current_location, path_info = heapq.heappop(priority_queue)
            
            # Skip if we've already found a better path to this location
            if current_location in visited and visited[current_location] <= current_cost:
                continue
                
            visited[current_location] = current_cost
            
            if show_steps:
                os.system('cls' if os.name == 'nt' else 'clear')
                current_name = self.locations.get(current_location, f"ID-{current_location}")
                print(f"STEP {step}: Exploring {current_name} 📍")
                print(f"Current cost: {current_cost:.1f} units")
                
                # Show current path
                path_display = " → ".join([
                    f"{self.locations.get(loc, f'ID-{loc}')}(₱{cost:.1f})" 
                    for loc, cost, _, _, _ in path_info
                ])
                print(f"Current path: {path_display}")
                print(f"Priority queue size: {len(priority_queue)}")
                print(f"Cities visited: {len(visited)}")
                
                # Show current totals
                if path_info:
                    _, _, total_dist, total_toll, _ = path_info[-1]
                    print(f"Total distance: {total_dist:.0f}km | Total tolls: ₱{total_toll:.0f}")
                
                self.display_network(visited=visited, current=current_location)
                time.sleep(delay)
            
            # Check if we reached the destination
            if current_location == goal:
                if show_steps:
                    print("\n🎉 DESTINATION REACHED! Welcome to your destination! 🎉")
                    goal_name = self.locations.get(goal, f"ID-{goal}")
                    print(f"Arrived at {goal_name} with optimal cost: {current_cost:.1f} units")
                
                # Calculate totals
                final_info = path_info[-1]
                total_distance = final_info[2]
                total_toll = final_info[3]
                
                return path_info, current_cost, total_distance, total_toll
            
            # Explore neighboring cities via highways
            if current_location in self.graph:
                neighbors = self.graph[current_location]
                
                if show_steps and neighbors:
                    current_name = self.locations.get(current_location, f"ID-{current_location}")
                    print(f"\nExploring highways from {current_name}:")
                
                for neighbor, edge_cost, distance, traffic, toll, highway in neighbors:
                    new_cost = current_cost + edge_cost
                    
                    # Only add to queue if we haven't visited or found a better path
                    if neighbor not in visited or visited[neighbor] > new_cost:
                        # Calculate cumulative totals
                        prev_distance = path_info[-1][2] if path_info else 0
                        prev_toll = path_info[-1][3] if path_info else 0
                        
                        new_path_info = path_info + [(
                            neighbor, 
                            new_cost, 
                            prev_distance + distance,
                            prev_toll + toll,
                            highway or "Local Road"
                        )]
                        
                        heapq.heappush(priority_queue, (new_cost, neighbor, new_path_info))
                        
                        if show_steps:
                            neighbor_name = self.locations.get(neighbor, f"ID-{neighbor}")
                            highway_info = f" via {highway}" if highway else ""
                            print(f"  → {neighbor_name}: new_cost={new_cost:.1f} "
                                  f"(+{edge_cost:.1f} from current){highway_info}")
                            print(f"     Distance: +{distance:.0f}km | Toll: +₱{toll:.0f}")
        
        start_name = self.locations.get(start, f"ID-{start}")
        goal_name = self.locations.get(goal, f"ID-{goal}")
        print(f"\n❌ No highway route found from {start_name} to {goal_name}!")
        return None, None, None, None
    
    def analyze_algorithm(self, path_info, total_cost, total_distance, total_toll):
        """Provide analysis of the UCS algorithm performance"""
        print("\n" + "="*80)
        print("🇵🇭 UCS ALGORITHM ANALYSIS - PHILIPPINE HIGHWAY NAVIGATION 🇵🇭")
        print("="*80)
        
        if path_info and total_cost is not None:
            print(f"✅ Optimal route found through the Philippines!")
            print(f"💰 Total optimization cost: {total_cost:.2f} units")
            print(f"🛣️  Total distance: {total_distance:.0f} kilometers")
            print(f"💵 Total toll fees: ₱{total_toll:.2f}")
            print(f"📍 Route includes: {len(path_info)} cities/locations")
            
            print(f"\n🗺️  Detailed Philippine Route:")
            for i, (location, cumulative_cost, cum_distance, cum_toll, highway) in enumerate(path_info):
                location_name = self.locations.get(location, f"ID-{location}")
                if i == 0:
                    print(f"   {i+1}. START: {location_name}")
                    print(f"       Starting point - Ready to explore the Philippines!")
                else:
                    prev_cost = path_info[i-1][1]
                    prev_distance = path_info[i-1][2]
                    prev_toll = path_info[i-1][3]
                    
                    segment_cost = cumulative_cost - prev_cost
                    segment_distance = cum_distance - prev_distance
                    segment_toll = cum_toll - prev_toll
                    
                    print(f"   {i+1}. {location_name}")
                    print(f"       Via: {highway}")
                    print(f"       Segment: {segment_distance:.0f}km, ₱{segment_toll:.0f} toll, "
                          f"cost +{segment_cost:.2f}")
                    print(f"       Total so far: {cum_distance:.0f}km, ₱{cum_toll:.0f}, "
                          f"cost {cumulative_cost:.2f}")
            
            print(f"\n🧭 Optimality: This is the minimum cost route through Philippine highways")
            print("   (UCS guarantees optimal solution considering distance, traffic, and tolls)")
            
            # Estimate travel time and fuel cost
            avg_speed = 60  # km/h average speed including traffic
            estimated_hours = total_distance / avg_speed
            fuel_cost = total_distance * 2.5  # Rough estimate: ₱2.5 per km
            
            print(f"\n⏱️  Estimated Travel Information:")
            print(f"   Travel time: {estimated_hours:.1f} hours ({estimated_hours//1:.0f}h {(estimated_hours%1)*60:.0f}min)")
            print(f"   Estimated fuel cost: ₱{fuel_cost:.0f}")
            print(f"   Total trip cost: ₱{total_toll + fuel_cost:.0f} (tolls + fuel)")
            
        else:
            print("❌ No route available through Philippine highway network")
        
        total_locations = len(self.locations)
        total_highways = sum(len(connections) for connections in self.graph.values()) // 2
        
        print(f"\n📊 Philippine Highway Network Analysis:")
        print(f"   Total cities/locations: {total_locations}")
        print(f"   Total highway connections: {total_highways}")
        print(f"   Network coverage: Luzon Island expressway system")
        
        print(f"\n🔍 UCS Algorithm Characteristics:")
        print(f"   Time Complexity: O((V + E) log V) with binary heap")
        print(f"   Space Complexity: O(V) for priority queue and visited set")
        print(f"   Completeness: ✅ (finds route if one exists)")
        print(f"   Optimality: ✅ (finds minimum cost route)")
        print(f"   Philippine-specific: ✅ (considers local traffic and toll patterns)")


def create_philippine_highway_scenarios():
    """Create Philippine highway navigation scenarios"""
    
    scenarios = {}
    
    # Scenario 1: Northern Luzon Expressway System
    scenario1 = PhilippineHighwayNavigatorUCS()
    
    # Add major Northern Luzon locations
    locations1 = {
        'MNL': 'Metro Manila',
        'PAM': 'Pampanga (Angeles/Clark)',
        'TAR': 'Tarlac City', 
        'SUB': 'Subic Bay',
        'PAN': 'Pangasinan (Dagupan)',
        'LAU': 'La Union (San Fernando)',
        'BAG': 'Baguio City'
    }
    
    for loc_id, name in locations1.items():
        scenario1.add_location(loc_id, name)
    
    # Add Northern Luzon highways with realistic data
    # NLEX: Manila to Pampanga
    scenario1.add_highway('MNL', 'PAM', 80, 1.3, 180, 'NLEX')
    
    # SCTEX: Pampanga to Tarlac and Subic
    scenario1.add_highway('PAM', 'TAR', 55, 1.1, 95, 'SCTEX')
    scenario1.add_highway('PAM', 'SUB', 45, 1.2, 85, 'SCTEX')
    
    # TPLEX: Tarlac to Pangasinan to La Union
    scenario1.add_highway('TAR', 'PAN', 70, 1.0, 120, 'TPLEX')
    scenario1.add_highway('PAN', 'LAU', 55, 1.1, 95, 'TPLEX')
    
    # Local roads and alternative routes
    scenario1.add_highway('LAU', 'BAG', 45, 1.8, 0, 'Kennon Road')
    scenario1.add_highway('TAR', 'BAG', 85, 1.5, 0, 'Tarlac-Baguio Road')
    scenario1.add_highway('MNL', 'SUB', 120, 2.0, 50, 'MacArthur Highway')
    
    scenarios["Northern Luzon Network"] = scenario1
    
    # Scenario 2: Southern Luzon Expressway System  
    scenario2 = PhilippineHighwayNavigatorUCS()
    
    locations2 = {
        'MNL': 'Metro Manila',
        'CAV': 'Cavite (Bacoor)',
        'LGB': 'Laguna (Biñan)',
        'STO': 'Sto. Tomas, Batangas',
        'BAT': 'Batangas City',
        'LOS': 'Los Baños, Laguna',
        'CAL': 'Calamba, Laguna'
    }
    
    for loc_id, name in locations2.items():
        scenario2.add_location(loc_id, name)
    
    # SLEX: Manila to Laguna to Batangas
    scenario2.add_highway('MNL', 'LGB', 45, 1.4, 140, 'SLEX')
    scenario2.add_highway('LGB', 'CAL', 25, 1.2, 60, 'SLEX')
    scenario2.add_highway('CAL', 'STO', 35, 1.1, 75, 'SLEX')
    
    # STAR Tollway: Sto. Tomas to Batangas City
    scenario2.add_highway('STO', 'BAT', 45, 1.0, 110, 'STAR Tollway')
    
    # CALAX: Cavite to Laguna
    scenario2.add_highway('CAV', 'LGB', 30, 1.3, 95, 'CALAX')
    
    # Local roads and alternatives
    scenario2.add_highway('MNL', 'CAV', 35, 1.6, 85, 'Coastal Road')
    scenario2.add_highway('LGB', 'LOS', 15, 1.1, 0, 'Local Road')
    scenario2.add_highway('CAL', 'LOS', 8, 1.0, 0, 'Local Road')
    scenario2.add_highway('MNL', 'CAL', 55, 1.8, 0, 'National Highway')
    
    scenarios["Southern Luzon Network"] = scenario2
    
    # Scenario 3: Complete Metro Manila & Luzon Network
    scenario3 = PhilippineHighwayNavigatorUCS()
    
    locations3 = {
        'MNL': 'Metro Manila',
        'QC': 'Quezon City',
        'MKT': 'Makati CBD',
        'BGC': 'Bonifacio Global City',
        'NAIA': 'NAIA Airport Area',
        'PAM': 'Pampanga (Clark)',
        'CAV': 'Cavite',
        'LGB': 'Laguna (Biñan)',
        'BAT': 'Batangas City',
        'SUB': 'Subic Bay'
    }
    
    for loc_id, name in locations3.items():
        scenario3.add_location(loc_id, name)
    
    # Metro Manila internal expressways
    scenario3.add_highway('MNL', 'QC', 20, 2.5, 45, 'EDSA/C5')
    scenario3.add_highway('MNL', 'MKT', 15, 2.8, 55, 'Skyway')
    scenario3.add_highway('MKT', 'BGC', 8, 2.0, 35, 'Skyway')
    scenario3.add_highway('MNL', 'NAIA', 12, 2.2, 40, 'NAIA Expressway')
    scenario3.add_highway('BGC', 'NAIA', 10, 1.8, 30, 'Skyway')
    
    # Major expressways from Metro Manila
    scenario3.add_highway('MNL', 'PAM', 80, 1.3, 180, 'NLEX')
    scenario3.add_highway('MNL', 'CAV', 35, 1.6, 85, 'Coastal Road')
    scenario3.add_highway('MNL', 'LGB', 45, 1.4, 140, 'SLEX')
    scenario3.add_highway('PAM', 'SUB', 45, 1.2, 85, 'SCTEX')
    scenario3.add_highway('LGB', 'BAT', 80, 1.1, 185, 'SLEX + STAR')
    scenario3.add_highway('CAV', 'LGB', 30, 1.3, 95, 'CALAX')
    
    scenarios["Complete Luzon Network"] = scenario3
    
    return scenarios


def main():
    """Main function to run the Philippine Highway navigation simulation"""
    print("🇵🇭 PHILIPPINE HIGHWAY NAVIGATOR 🇵🇭")
    print("Using Uniform Cost Search (UCS) Algorithm")
    print("Navigate through Luzon's major expressways!")
    print("="*80)
    
    scenarios = create_philippine_highway_scenarios()
    
    print("\nAvailable Philippine highway scenarios:")
    for i, (name, _) in enumerate(scenarios.items(), 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input("\nSelect scenario (1-3): ")) - 1
        scenario_name = list(scenarios.keys())[choice]
        highway_system = scenarios[scenario_name]
        
        print(f"\n🏖️ Selected: {scenario_name}")
        print("Featuring major Philippine expressways and highways!")
        
        # Display available locations
        print("\nAvailable cities and locations:")
        for loc_id, name in highway_system.locations.items():
            print(f"  {loc_id}: {name}")
        
        # Get start and destination
        start = input("\nEnter starting location ID: ").strip().upper()
        goal = input("Enter destination location ID: ").strip().upper()
        
        if start not in highway_system.locations or goal not in highway_system.locations:
            print("❌ Invalid location ID. Please use the IDs shown above.")
            return
        
        # Display initial network
        print(f"\n🗺️  Philippine Highway Network Overview:")
        highway_system.display_network()
        
        # Ask user for simulation preferences
        show_steps = input("\nShow step-by-step navigation process? (y/n): ").lower() == 'y'
        delay = 0.8
        if show_steps:
            try:
                delay = float(input("Animation delay in seconds (default 0.8): ") or "0.8")
            except ValueError:
                delay = 0.8
        
        start_name = highway_system.locations[start]
        goal_name = highway_system.locations[goal]
        print(f"\n🚀 Calculating optimal route from {start_name} to {goal_name}")
        print("Considering Philippine traffic patterns, toll costs, and distances...")
        
        # Run UCS search
        solution_path, total_cost, total_distance, total_toll = highway_system.ucs_search(
            start, goal, show_steps=show_steps, delay=delay
        )
        
        # Analyze results
        highway_system.analyze_algorithm(solution_path, total_cost, total_distance, total_toll)
        
        # Final display
        if solution_path and total_cost is not None:
            print(f"\n🎯 Navigation Complete! Mabuhay! 🎯")
            print(f"📱 Route Summary: {total_distance:.0f}km journey with ₱{total_toll:.0f} in tolls")
            print("🛣️ Safe travels through the beautiful Philippines!")
            highway_system.display_network(path=solution_path)
            
            # Travel tips
            print(f"\n💡 Travel Tips:")
            print(f"   • Bring exact change for toll booths")
            print(f"   • Check traffic updates via Waze or Google Maps")
            print(f"   • Consider peak hours: 6-9 AM and 5-8 PM")
            print(f"   • Have your driver's license and registration ready")
        
    except (ValueError, IndexError):
        print("❌ Invalid selection. Please run the program again.")
    except KeyboardInterrupt:
        print("\n\n⏹️ Navigation interrupted. Drive safely!")


if __name__ == "__main__":
    main()