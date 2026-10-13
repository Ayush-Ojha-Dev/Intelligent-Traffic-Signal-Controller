from app.services import oracle_service


def main():
    print("\n=== Oracle Vehicle Counts ===")

    vehicle_counts = oracle_service.get_vehicle_counts()

    for row in vehicle_counts:
        print(row)

    print("\n=== Oracle Signals ===")

    signals = oracle_service.get_signals()

    for row in signals:
        print(row)

    print("\n=== Oracle Cameras ===")

    cameras = oracle_service.get_cameras()

    for row in cameras:
        print(row)


if __name__ == "__main__":
    main()
