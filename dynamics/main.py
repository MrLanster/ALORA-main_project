from dynamics import dynamics,shoulder1

while True:
        print("Enter angles for the servos (0-180):")
        user_input = input("Format: shoulder1 elbow wrist fingers (e.g., 90 90 90 90): ")
        try:
            angles = list(map(int, user_input.split()))
            if len(angles) == 4 and all(0 <= angle <= 180 for angle in angles):
                dynamics.control_servos({
                    'shoulder1': angles[0],
                    'elbow': angles[1],
                    'wrist': angles[2],
                    'fingers': angles[3]
                })
            else:
                print("Invalid input. Please enter four numeric values between 0 and 180.")
        except ValueError:
            print("Invalid input. Please enter four numeric values separated by spaces.")