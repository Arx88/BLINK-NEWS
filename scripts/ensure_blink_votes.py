import os
import json

def ensure_votes_in_blinks():
    """
    Ensures that 'positive_votes' and 'negative_votes' fields exist and are integers
    in all blink JSON files. Defaults to 0 if missing or invalid.
    """
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    blinks_dir = os.path.join(project_root, 'data', 'blinks')

    if not os.path.isdir(blinks_dir):
        print(f"Error: Blinks directory not found at {blinks_dir}")
        return

    print(f"Scanning blink files in: {blinks_dir}")
    processed_files = 0
    modified_files_count = 0

    for filename in os.listdir(blinks_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(blinks_dir, filename)
            print(f"Processing {filepath}...")
            processed_files += 1
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    blink_data = json.load(f)

                made_changes = False
                log_messages = []

                # Check and fix positive_votes
                if not isinstance(blink_data.get('positive_votes'), int):
                    old_value = blink_data.get('positive_votes', 'Not present')
                    blink_data['positive_votes'] = 0
                    log_messages.append(f"  - Set 'positive_votes' to 0 (was {old_value})")
                    made_changes = True

                # Check and fix negative_votes
                if not isinstance(blink_data.get('negative_votes'), int):
                    old_value = blink_data.get('negative_votes', 'Not present')
                    blink_data['negative_votes'] = 0
                    log_messages.append(f"  - Set 'negative_votes' to 0 (was {old_value})")
                    made_changes = True

                if made_changes:
                    modified_files_count += 1
                    print(f"Modifications made to {filename}:")
                    for msg in log_messages:
                        print(msg)
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(blink_data, f, indent=4, ensure_ascii=False)
                        print(f"  Successfully updated {filename}")
                    except IOError as e:
                        print(f"  Error writing updates to {filename}: {e}")
                else:
                    print(f"  No changes needed for {filename}.")

            except json.JSONDecodeError as e:
                print(f"  Error decoding JSON from {filename}: {e}")
            except IOError as e:
                print(f"  Error reading file {filename}: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred with {filename}: {e}")

    print(f"\n--- Script Summary ---")
    print(f"Total files processed: {processed_files}")
    print(f"Total files modified: {modified_files_count}")
    if processed_files == 0:
        print("No JSON files found in the directory.")
    print("--- End of Script ---")

if __name__ == "__main__":
    ensure_votes_in_blinks()
