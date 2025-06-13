import re
from models.blink_generator import BlinkGenerator
import ollama # For ollama.ResponseError
import requests # For requests.exceptions.ConnectionError
import httpx # For httpx.ConnectError

# 1. Instantiate BlinkGenerator
blink_generator = BlinkGenerator()

# 2. Define sample news title and text
sample_title = "Scientists Discover New Quantum Entanglement Phenomenon with Potential for Unbreakable Encryption"
sample_text_with_reasoning_and_points = """This is a groundbreaking discovery. We need to analyze the implications for various fields.
The potential for unbreakable encryption is particularly exciting.
Let's break down the key findings:
- First key finding about the new quantum entanglement.
- Second key finding detailing specifics of the phenomenon.
- Third key finding on its observed properties.
- Fourth key finding regarding potential applications.
- Fifth key finding about future research directions.
- This could also impact quantum computing.
- Further validation studies are planned.
"""

num_points_to_extract = 5

print(f"Attempting to generate summary for: '{sample_title}'")

try:
    # 3. Call generate_ollama_summary
    points = blink_generator.generate_ollama_summary(sample_text_with_reasoning_and_points, sample_title, num_points_to_extract)

    print("\nGenerated points (from Ollama if available):")
    if points:
        for i, point in enumerate(points):
            print(f"{i+1}. {point}")
    else:
        print("No points were generated.")

    # Check if the returned points are the fallback points
    # This indicates Ollama failed and the main function used its fallback.
    # We need to generate what the fallback points would look like for comparison.
    # Note: This relies on the test script knowing how fallback points are generated,
    # or calling the fallback generation method itself.

    # For a more robust check, we might need to see if an error was logged
    # or if the generate_ollama_summary could return a status.
    # Given the current structure, we'll check if the points match the known fallback structure.

    # A simpler way: if the connection fails, generate_ollama_summary prints
    # "Error inesperado al generar resumen con Ollama:" or "Error al comunicarse con Ollama:"
    # and returns fallback points.
    # The test script's goal is to test the NEW parsing logic if Ollama is down.

    # Let's try to call Ollama, and if it fails (indicated by returned fallback points),
    # then we proceed to test the parsing logic with mock_ollama_output.

    expected_fallback_if_ollama_failed = blink_generator.generate_fallback_points(sample_title, num_points_to_extract)

    if points == expected_fallback_if_ollama_failed:
        print(f"\nOllama call failed or returned fallback points. Will now test parsing logic with mock data.")

        mock_ollama_output = """Okay, I need to extract 5 points. Here's my thinking process.
This article is about quantum entanglement.
It has several implications.
The main points are:
* Mock point 1 from simulated response.
* Mock point 2, another detail.
* Mock point 3 about applications.
* Mock point 4 on future work.
* Mock point 5, a concluding remark.
This should be enough.
"""

        print("\nSimulating Ollama response:")
        print("--------------------")
        print(mock_ollama_output)
        print("--------------------")

        all_lines = mock_ollama_output.strip().split('\n')
        extracted_points_from_mock = []

        for line in reversed(all_lines):
            cleaned_line = re.sub(r'^\s*[\*\-•\d\.]+\s*', '', line).strip()
            if cleaned_line:
                extracted_points_from_mock.insert(0, cleaned_line)
            if len(extracted_points_from_mock) == num_points_to_extract:
                break

        points_from_mock_parsing = extracted_points_from_mock

        if len(points_from_mock_parsing) < num_points_to_extract:
            missing_count = num_points_to_extract - len(points_from_mock_parsing)
            print(f"Mock parsing resulted in {len(points_from_mock_parsing)} points, need {missing_count} more from fallback.")
            fallback_fill = blink_generator.generate_fallback_points(sample_title, missing_count)
            points_from_mock_parsing.extend(fallback_fill)
        elif len(points_from_mock_parsing) > num_points_to_extract:
            points_from_mock_parsing = points_from_mock_parsing[:num_points_to_extract]

        print("\nGenerated points (from MOCK data and new parsing logic):")
        if points_from_mock_parsing:
            for i, point in enumerate(points_from_mock_parsing):
                print(f"{i+1}. {point}")
        else:
            print("No points were generated from mock data.")

except (ollama.ResponseError, requests.exceptions.ConnectionError, httpx.ConnectError) as e:
    # This block might not be hit if generate_ollama_summary handles all exceptions
    # and returns fallback points. The logic above handles that.
    # This is a secondary catch.
    print(f"\nOllama specific error caught ({type(e).__name__}): {e}")
    print("This indicates an issue before fallback logic in generate_ollama_summary or a direct ollama lib error.")
    print("Consider if the main function should re-raise or if this test needs adjustment.")
    # For now, we can also run the mock test here as a safety measure.
    mock_ollama_output = """[Error Path] Okay, I need to extract 5 points. Here's my thinking process.
This article is about quantum entanglement.
It has several implications.
The main points are:
* Mock point 1 (error path).
* Mock point 2 (error path).
* Mock point 3 (error path).
* Mock point 4 (error path).
* Mock point 5 (error path).
This should be enough.
"""
    all_lines = mock_ollama_output.strip().split('\n')
    extracted_points_error_path = []
    for line in reversed(all_lines):
        cleaned_line = re.sub(r'^\s*[\*\-•\d\.]+\s*', '', line).strip()
        if cleaned_line:
            extracted_points_error_path.insert(0, cleaned_line)
        if len(extracted_points_error_path) == num_points_to_extract:
            break
    points_from_error_mock = extracted_points_error_path
    # Fallback logic
    if len(points_from_error_mock) < num_points_to_extract:
        points_from_error_mock.extend([f"Fallback point {i+1}" for i in range(num_points_to_extract - len(points_from_error_mock))])

    print("\nGenerated points (from MOCK data in error path and new parsing logic):")
    for i, point in enumerate(points_from_error_mock):
        print(f"{i+1}. {point}")


except Exception as e:
    print(f"\nAn unexpected error occurred in test script: {e}")
    import traceback
    traceback.print_exc()
