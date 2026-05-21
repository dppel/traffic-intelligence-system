import sys
from collections import Counter
from dataclasses import dataclass

# Import from src.tracker
from src.tracker import TrackedVehicle
from src.counter import VehicleCounter

def create_mock_vehicle(track_id: int, center: tuple[int, int], label: str = "car") -> TrackedVehicle:
    # Build box around center
    x, y = center
    box = (x - 10, y - 10, x + 10, y + 10)
    return TrackedVehicle(
        track_id=track_id,
        class_id=2, # standard COCO car id
        label=label,
        confidence=0.95,
        box=box,
        center=center,
        speed_pixels_per_frame=2.0
    )

def run_tests():
    print("==================================================")
    print("Starting Segment Crossing & Directional Flow Tests")
    print("==================================================")

    # 1. Setup Counter with tripwire
    # Horizontal line at y=100 from x=0 to x=200
    counter = VehicleCounter(counting_line=((0, 100), (200, 100)))

    # 2. Test Downward Crossing (Incoming: dy > 0)
    print("\nTest 1: Downward crossing (Incoming)...")
    # Vehicle moving from (50, 90) to (50, 110) - crosses y=100 downward
    vehicle_incoming = create_mock_vehicle(track_id=1, center=(50, 90))
    counter.update([vehicle_incoming])
    print(f"Frame 1 - Centroid: {vehicle_incoming.center}, Crossed: {counter.crossed_ids}, Unique: {counter.total_unique}")

    vehicle_incoming2 = create_mock_vehicle(track_id=1, center=(50, 110))
    counter.update([vehicle_incoming2])
    print(f"Frame 2 - Centroid: {vehicle_incoming2.center}, Crossed: {counter.crossed_ids}, Unique: {counter.total_unique}")
    print(f"Incoming: {counter.incoming_count}, Outgoing: {counter.outgoing_count}")
    assert 1 in counter.crossed_ids
    assert counter.incoming_count == 1
    assert counter.outgoing_count == 0

    # 3. Test Upward Crossing (Outgoing: dy <= 0)
    print("\nTest 2: Upward crossing (Outgoing)...")
    # Vehicle moving from (150, 115) to (150, 85) - crosses y=100 upward
    vehicle_outgoing = create_mock_vehicle(track_id=2, center=(150, 115))
    counter.update([vehicle_outgoing])
    print(f"Frame 1 - Centroid: {vehicle_outgoing.center}, Crossed: {counter.crossed_ids}, Unique: {counter.total_unique}")

    vehicle_outgoing2 = create_mock_vehicle(track_id=2, center=(150, 85))
    counter.update([vehicle_outgoing2])
    print(f"Frame 2 - Centroid: {vehicle_outgoing2.center}, Crossed: {counter.crossed_ids}, Unique: {counter.total_unique}")
    print(f"Incoming: {counter.incoming_count}, Outgoing: {counter.outgoing_count}")
    assert 2 in counter.crossed_ids
    assert counter.incoming_count == 1
    assert counter.outgoing_count == 1

    # 4. Test Non-Crossing (Static/Parked or parallel movement)
    print("\nTest 3: Non-crossing (Static vehicle)...")
    # Static vehicle staying at (100, 80)
    vehicle_static = create_mock_vehicle(track_id=3, center=(100, 80), label="truck")
    counter.update([vehicle_static])
    counter.update([vehicle_static])
    print(f"Static vehicle - Crossed: {counter.crossed_ids}, Unique: {counter.total_unique}")
    assert 3 not in counter.crossed_ids

    # 5. Parallel Movement above the line
    print("\nTest 4: Parallel movement (No crossing)...")
    # Vehicle moving from (10, 50) to (190, 50) - parallel to y=100 but never crosses
    vehicle_parallel1 = create_mock_vehicle(track_id=4, center=(10, 50), label="motorcycle")
    counter.update([vehicle_parallel1])
    vehicle_parallel2 = create_mock_vehicle(track_id=4, center=(190, 50), label="motorcycle")
    counter.update([vehicle_parallel2])
    print(f"Parallel vehicle - Crossed: {counter.crossed_ids}, Unique: {counter.total_unique}")
    assert 4 not in counter.crossed_ids

    # Summary
    print("\n==================================================")
    print("Tests Completed successfully! All checks passed.")
    print(f"Total Unique: {counter.total_unique}")
    print(f"Summary: {counter.summary()}")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
