import random
import json
import os
import cv2
from DrawCube import draw_cube

class CubeQuestionGenerator:
    def __init__(self):
        # Content dictionary - contains all possible characters
        self.CONTENT_DICT = [
            # Letters
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            # Numbers
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
            # Four special shapes
            "circle",         # Solid circle
            "circle_hollow",  # Hollow circle
            "square",         # Solid square
            "square_hollow"   # Hollow square
        ]
        self.CONTENT_SAME = ["O", "X", "circle", "circle_hollow", "square",  "square_hollow"]
        # Rotation angle options
        self.ROTATIONS = [0, 90, 180, 270]
        
        # Cube face mapping table - hardcoded version
        # Format: (front_face, front_rotation): (up_face, up_rotation, right_face, right_rotation)
        self.FACE_MAPPING = {
            (1, 0): (5, 0, 3, 270),
            (2, 0): (1, 0, 3, 0),
            (3, 0): (1, 90, 5, 180),
            (4, 0): (2, 0, 3, 90),
            (5, 0): (4, 0, 3, 180),
            (6, 0): (1, 270, 2, 0),
            (1, 180): (2, 180, 6, 270),
            (2, 180): (4, 180, 6, 180),
            (3, 180): (4, 90, 2, 180),
            (4, 180): (5, 180, 6, 90),
            (5, 180): (1, 180, 6, 0),
            (6, 180): (4, 270, 5, 0),
            (1, 270): (3, 180, 2, 270),
            (2, 270): (3, 270, 4, 270),
            (3, 270): (5, 90, 4, 180),
            (4, 270): (3, 0, 5, 270),
            (5, 270): (3, 90, 1, 270),
            (6, 270): (2, 270, 4, 0),
            (1, 90): (6, 180, 5, 90),
            (2, 90): (6, 90, 1, 90),
            (3, 90): (2, 90, 1, 180),
            (4, 90): (6, 0, 2, 90),
            (5, 90): (6, 270, 4, 90),
            (6, 90): (5, 270, 1, 0)
        }
        
        # Output directory
        self.output_dir = "Images"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def display_mapping_summary(self):
        """Display mapping table summary information"""
        print("\nMapping table summary:")
        print("=" * 60)
        print(f"Total loaded {len(self.FACE_MAPPING)} mapping relationships")
        print("Format: front face(rotation°) → up face(rotation°), right face(rotation°)")
        print("-" * 60)
        
        if self.FACE_MAPPING:
            # Sort by front face number for display
            sorted_mappings = sorted(self.FACE_MAPPING.items(), key=lambda x: (x[0][0], x[0][1]))
            
            for i, ((front_face, front_rot), (up_face, up_rot, right_face, right_rot)) in enumerate(sorted_mappings[:10]):  # Only show first 10
                print(f"{i+1:2d}. Face{front_face}({front_rot:3d}°) → Face{up_face}({up_rot:3d}°), Face{right_face}({right_rot:3d}°)")
            
            if len(self.FACE_MAPPING) > 10:
                print(f"... {len(self.FACE_MAPPING) - 10} more mapping relationships")
        else:
            print("No mapping relationships loaded")
        
        print("=" * 60)

    def create_cube_faces(self):
        """Create 6 faces of a cube, each face has unique content"""
        selected_contents = random.sample(self.CONTENT_DICT, 6)
        cube_faces = {}
        for i in range(1, 7):
            cube_faces[i] = {
                'content': selected_contents[i-1],
                'rotation': random.choice(self.ROTATIONS)
            }
        return cube_faces
    
    def get_visible_faces(self, cube_faces, front_face_num, front_rotation):
        """
        Get up and right face information based on front face number and rotation angle
        Use FACE_MAPPING to determine correct mapping relationships
        """
        if not self.FACE_MAPPING:
            print("Warning: FACE_MAPPING is empty, using default mapping")
            # Default simple mapping (for testing only)
            up_face_num = (front_face_num % 6) + 1
            right_face_num = ((front_face_num + 1) % 6) + 1
            up_rotation = 0
            right_rotation = 0
        else:
            if (front_face_num, front_rotation) in self.FACE_MAPPING:
                up_face_num, up_rotation, right_face_num, right_rotation = self.FACE_MAPPING[(front_face_num, front_rotation)]
            else:
                print(f"Warning: Mapping not found for ({front_face_num}, {front_rotation})")
                up_face_num = (front_face_num % 6) + 1
                right_face_num = ((front_face_num + 1) % 6) + 1
                up_rotation = 0
                right_rotation = 0
        
        # Get actual face content and rotation angles
        front_content = cube_faces[front_face_num]['content']
        front_rot = (cube_faces[front_face_num]['rotation'] + front_rotation) % 360
        
        up_content = cube_faces[up_face_num]['content']
        up_rot = (cube_faces[up_face_num]['rotation'] + up_rotation) % 360
        
        right_content = cube_faces[right_face_num]['content']
        right_rot = (cube_faces[right_face_num]['rotation'] + right_rotation) % 360
        
        return {
            'front': {'content': front_content, 'rotation': front_rot, 'face_num': front_face_num},
            'up': {'content': up_content, 'rotation': up_rot, 'face_num': up_face_num},
            'right': {'content': right_content, 'rotation': right_rot, 'face_num': right_face_num}
        }

    def count_same_faces(self, visible_1, visible_2):
        """Calculate the number of same face numbers between two viewing angles"""
        # Get the visible face numbers from both viewing angles
        faces_1 = {visible_1['front']['face_num'], visible_1['up']['face_num'], visible_1['right']['face_num']}
        faces_2 = {visible_2['front']['face_num'], visible_2['up']['face_num'], visible_2['right']['face_num']}
        
        # Calculate intersection (number of same face numbers)
        same_count = len(faces_1.intersection(faces_2))
        
        return same_count

    def find_configs_with_same_faces(self, cube_faces, target_same_count):
        """Find configuration pairs with specified number of same faces"""
        available_configs = list(self.FACE_MAPPING.keys())
        max_attempts = 1000
        
        for _ in range(max_attempts):
            config_1 = random.choice(available_configs)
            config_2 = random.choice(available_configs)
            
            if config_1 == config_2:
                continue
                
            visible_1 = self.get_visible_faces(cube_faces, config_1[0], config_1[1])
            visible_2 = self.get_visible_faces(cube_faces, config_2[0], config_2[1])
            
            same_count = self.count_same_faces(visible_1, visible_2)
            
            if same_count == target_same_count:
                return config_1, config_2, visible_1, visible_2
        
        # If no suitable configuration found, return random configurations
        print(f"Warning: Could not find configs with {target_same_count} same faces, using random configs")
        config_1 = random.choice(available_configs)
        config_2 = random.choice([c for c in available_configs if c != config_1])
        visible_1 = self.get_visible_faces(cube_faces, config_1[0], config_1[1])
        visible_2 = self.get_visible_faces(cube_faces, config_2[0], config_2[1])
        return config_1, config_2, visible_1, visible_2
    def generate_same_question_with_faces(self, question_num, same_face_count):
        """Generate same cube question with specified number of same faces"""
        cube_faces = self.create_cube_faces()
        
        config_1, config_2, visible_1, visible_2 = self.find_configs_with_same_faces(
            cube_faces, same_face_count)
        
        actual_same_count = self.count_same_faces(visible_1, visible_2)
        
        # Generate images
        self.generate_cube_image(visible_1, f"{question_num}-0.jpg")
        self.generate_cube_image(visible_2, f"{question_num}-1.jpg")
        
        # Save detailed information
        question_data = {
            'question_type': 'Same',
            'same_face_count': actual_same_count,
            'target_same_count': same_face_count,
            'cube_faces': cube_faces,
            'view_1': {
                'config': config_1,
                'visible_faces': visible_1
            },
            'view_2': {
                'config': config_2,
                'visible_faces': visible_2
            }
        }
        
        with open(os.path.join(self.output_dir, f"question_{question_num}_data.json"), "w", encoding="utf-8") as f:
            json.dump(question_data, f, ensure_ascii=False, indent=2)
        
        return "S", cube_faces, visible_1, visible_2
    
    def generate_different_question_content_change(self, question_num, fixed_faces=None):
        """
        Generate different cube question: first find configs with same visible faces like same_3_faces, 
        then modify one face content
        """
        # Create first cube
        cube_faces_1 = self.create_cube_faces()
        
        # Find two different configs that show the same 3 faces (like same_3_faces)
        config_1, config_2, visible_1_original, visible_2_original = self.find_configs_with_same_faces(
            cube_faces_1, 3)
        
        # If we can't find 3 same faces, try 2 same faces
        if self.count_same_faces(visible_1_original, visible_2_original) < 2:
            config_1, config_2, visible_1_original, visible_2_original = self.find_configs_with_same_faces(
                cube_faces_1, 2)
        
        print(f"Found configs with {self.count_same_faces(visible_1_original, visible_2_original)} same faces")
        
        # Create second cube (copy first one)
        cube_faces_2 = {k: v.copy() for k, v in cube_faces_1.items()}
        
        # Determine which face to modify from the visible faces in config_2
        visible_face_nums_2 = [
            visible_2_original['front']['face_num'],
            visible_2_original['up']['face_num'], 
            visible_2_original['right']['face_num']
        ]
        
        # Choose one of the visible faces to modify
        changing_face_num = random.choice(visible_face_nums_2)
        
        # Get contents used by first cube
        used_contents = [cube_faces_1[i]['content'] for i in range(1, 7)]
        available_contents = [c for c in self.CONTENT_DICT if c not in used_contents]
        
        if available_contents:
            # Modify specified face content
            original_content = cube_faces_2[changing_face_num]['content']
            cube_faces_2[changing_face_num]['content'] = random.choice(available_contents)
            cube_faces_2[changing_face_num]['rotation'] = random.choice(self.ROTATIONS)
            print(f"Modified face {changing_face_num}: {original_content} -> {cube_faces_2[changing_face_num]['content']}")
        else:
            # If no available content, choose different one from used contents
            other_contents = [c for c in used_contents if c != cube_faces_1[changing_face_num]['content']]
            if other_contents:
                original_content = cube_faces_2[changing_face_num]['content']
                cube_faces_2[changing_face_num]['content'] = random.choice(other_contents)
                cube_faces_2[changing_face_num]['rotation'] = random.choice(self.ROTATIONS)
                print(f"Modified face {changing_face_num}: {original_content} -> {cube_faces_2[changing_face_num]['content']}")
        
        # Generate visible faces for both configs
        visible_1 = self.get_visible_faces(cube_faces_1, config_1[0], config_1[1])
        visible_2 = self.get_visible_faces(cube_faces_2, config_2[0], config_2[1])
        
        # Determine which position the modified face appears in
        modified_position = None
        for position in ['front', 'up', 'right']:
            if visible_2[position]['face_num'] == changing_face_num:
                modified_position = position
                break
        
        print(f"Modified face {changing_face_num} appears at position: {modified_position}")
        print(f"Config 1: Face{config_1[0]}(rot{config_1[1]})")
        print(f"Config 2: Face{config_2[0]}(rot{config_2[1]})")
        
        # Generate images
        self.generate_cube_image(visible_1, f"{question_num}-0.jpg")
        self.generate_cube_image(visible_2, f"{question_num}-1.jpg")
        
        # Save detailed information
        question_data = {
            'question_type': 'Different_Content_Change',
            'method': 'same_faces_then_modify',
            'original_same_faces': self.count_same_faces(visible_1_original, visible_2_original),
            'changing_face_num': changing_face_num,
            'modified_position': modified_position,
            'cube_faces_1': cube_faces_1,
            'cube_faces_2': cube_faces_2,
            'view_1': {
                'config': config_1,
                'visible_faces': visible_1
            },
            'view_2': {
                'config': config_2,
                'visible_faces': visible_2
            }
        }
        
        with open(os.path.join(self.output_dir, f"question_{question_num}_data.json"), "w", encoding="utf-8") as f:
            json.dump(question_data, f, ensure_ascii=False, indent=2)
        
        return "D", cube_faces_1, visible_1, visible_2

    def generate_different_question_rotation_only(self, question_num):
        """Generate different cube question: create difference only through rotation"""
        # Create first cube
        cube_faces_1 = self.create_cube_faces()
        
        # Ensure at least one visible face uses non-center-symmetric content
        non_symmetric_contents = [c for c in self.CONTENT_DICT if c not in self.CONTENT_SAME]
        
        # If cube doesn't have enough non-symmetric content, regenerate
        cube_non_symmetric = [face['content'] for face in cube_faces_1.values() 
                             if face['content'] in non_symmetric_contents]
        
        if len(cube_non_symmetric) < 1:
            # Force add at least one non-symmetric content
            face_to_modify = random.randint(1, 6)
            cube_faces_1[face_to_modify]['content'] = random.choice(non_symmetric_contents)
        
        config_1 = random.choice(list(self.FACE_MAPPING.keys()))
        visible_1 = self.get_visible_faces(cube_faces_1, config_1[0], config_1[1])
        
        # Create second cube (same content, different rotation)
        cube_faces_2 = {}
        for i in range(1, 7):
            cube_faces_2[i] = {
                'content': cube_faces_1[i]['content'],
                'rotation': cube_faces_1[i]['rotation']
            }
        
        # Modify rotation angles for some faces (only non-symmetric content)
        faces_to_rotate = []
        for i in range(1, 7):
            if cube_faces_2[i]['content'] not in self.CONTENT_SAME:
                faces_to_rotate.append(i)
        
        if faces_to_rotate:
            # Randomly select 1-2 faces to rotate
            num_faces_to_rotate = random.randint(1, min(2, len(faces_to_rotate)))
            selected_faces = random.sample(faces_to_rotate, num_faces_to_rotate)
            
            for face_num in selected_faces:
                # Choose a different rotation angle
                current_rotation = cube_faces_2[face_num]['rotation']
                available_rotations = [r for r in self.ROTATIONS if r != current_rotation]
                if available_rotations:
                    cube_faces_2[face_num]['rotation'] = random.choice(available_rotations)
        
        config_2 = random.choice(list(self.FACE_MAPPING.keys()))
        visible_2 = self.get_visible_faces(cube_faces_2, config_2[0], config_2[1])
        
        # Generate images
        self.generate_cube_image(visible_1, f"{question_num}-0.jpg")
        self.generate_cube_image(visible_2, f"{question_num}-1.jpg")
        
        # Save detailed information
        question_data = {
            'question_type': 'Different_Rotation_Only',
            'cube_faces_1': cube_faces_1,
            'cube_faces_2': cube_faces_2,
            'view_1': {
                'config': config_1,
                'visible_faces': visible_1
            },
            'view_2': {
                'config': config_2,
                'visible_faces': visible_2
            }
        }
        
        with open(os.path.join(self.output_dir, f"question_{question_num}_data.json"), "w", encoding="utf-8") as f:
            json.dump(question_data, f, ensure_ascii=False, indent=2)
        
        return "D", cube_faces_1, visible_1, visible_2
    
    def generate_cube_image(self, visible_faces, filename):
        """Generate cube image"""
        cube_img = draw_cube(
            up_text=visible_faces['up']['content'],
            front_text=visible_faces['front']['content'],
            right_text=visible_faces['right']['content'],
            up_rot=visible_faces['up']['rotation'],
            front_rot=visible_faces['front']['rotation'],
            right_rot=visible_faces['right']['rotation'],
            size=300,
            offset_ratio=0.35,
            text_color=(0, 0, 0),
            font_scale=7
        )
        
        filepath = os.path.join(self.output_dir, filename)
        cv2.imwrite(filepath, cube_img)
        print(f"Generated: {filename}")
    
    def generate_questions(self, question_counts):
        """
        Generate specified number of questions for each type
        question_counts: dict with keys like 'same_0_faces', 'same_1_faces', etc.
        """
        questions = []
        answers = []
        
        # Create question type list
        question_types = []
        
        # Add same cube with different face counts
        for i in range(4):  # 0, 1, 2, 3 faces
            count = question_counts.get(f'same_{i}_faces', 0)
            question_types.extend([f'same_{i}_faces'] * count)
        
        # Add different cube types
        count_diff_content = question_counts.get('different_content', 0)
        question_types.extend(['different_content'] * count_diff_content)
        
        count_diff_rotation = question_counts.get('different_rotation', 0)
        question_types.extend(['different_rotation'] * count_diff_rotation)
        
        # Shuffle order
        random.shuffle(question_types)
        
        total_questions = len(question_types)
        
        for i, q_type in enumerate(question_types, 1):
            print(f"Generating question {i}/{total_questions} - Type: {q_type}")
            
            if q_type.startswith('same_'):
                # Extract same face count
                same_face_count = int(q_type.split('_')[1])
                answer, cube1, visible1, visible2 = self.generate_same_question_with_faces(i, same_face_count)
            elif q_type == 'different_content':
                answer, cube1, visible1, visible2 = self.generate_different_question_content_change(i)
            elif q_type == 'different_rotation':
                answer, cube1, visible1, visible2 = self.generate_different_question_rotation_only(i)
            
            questions.append([f"./Images/{i}-0.jpg", f"./Images/{i}-1.jpg"])
            answers.append([answer])
        
        # Save meta.json file in the required format
        result = {
            "S2": {
                "Name": "Cube-Comparisons-Test",
                "Example": [
                    [
                        "Text",
                        "Compare the two cubes in the pair below."
                    ],
                    [
                        "Image",
                        "../../Images/S2-Cube-Comparisons-Test/Example/1.jpg"
                    ],
                    [
                        "Text",
                        "The pair is different because they must be drawings of different cubes. If the left cube is turned so that the A is upright and facing you, the N would be to the left of the A and hidden, not to the right of the A as is shown on the right hand member of the pair. Thus, the drawings must be of different cubes. Compare the two cubes in the pair below."
                    ],
                    [
                        "Image",
                        "../../Images/S2-Cube-Comparisons-Test/Example/2.jpg"
                    ],
                    [
                        "Text",
                        "The pair is the same because they could be drawings of the same cube. That is, if the A is turned on its side the X becomes hidden, the B is now on top, and the C (which was hidden) now appears. Thus the two drawings could be of the same cube. Compare the two cubes in the pair below."
                    ],
                    [
                        "Image",
                        "../../Images/S2-Cube-Comparisons-Test/Example/3.jpg"
                    ],
                    [
                        "Text",
                        "The pair is different because the X cannot be at the peak of the A on the left hand drawing and at the base of the A on the right hand drawing. Compare the two cubes in the pair below."
                    ],
                    [
                        "Image",
                        "../../Images/S2-Cube-Comparisons-Test/Example/4.jpg"
                    ],
                    [
                        "Text",
                        "The pair is different because P has its side next to G on the left hand cube but its top next to G on the right hand cube. Compare the two cubes in the pair below."
                    ],
                    [
                        "Image",
                        "../../Images/S2-Cube-Comparisons-Test/Example/5.jpg"
                    ],
                    [
                        "Text",
                        "The pair is the same because the J and K are just turned on their side, moving the O to the top."
                    ]
                ],
                "Group": {
                    "Description": "Wooden blocks such as children play with are often cubical with a different letter, number, or symbol on each of the six faces (top, bottom, four sides). Each problem in this test consists of drawings of pairs of cubes or blocks of this kind. Remember, there is a different design, number, or letter on each face of a given cube or block. Note: No letters, numbers, or symbols appear on more than one face of a given cube. Except for that, any letter, number or symbol can be on the hidden faces of a cube. You are to decide whether the two cubes are the same or different after applying some rotations.",
                    "Instruction": "For the question below: Answer \"S\" if the two cubes are the same. Answer \"D\" if the two cubes are different. Please provide your answer in the following JSON format: {\"answer\": \"S_or_D\"}.",
                    "Answers": answers,
                    "Questions": questions
                }
            }
        }
        
        with open("meta.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\nGeneration completed!")
        print(f"Total questions: {total_questions}")
        for q_type, count in question_counts.items():
            if count > 0:
                print(f"{q_type}: {count}")
        print(f"Files saved in: {self.output_dir}/")
        print(f"meta.json saved in current directory")

def main():
    generator = CubeQuestionGenerator()
    
    print("Cube Question Generator")
    print("=" * 50)
    print(f"Loaded {len(generator.FACE_MAPPING)} cube face mapping relationships")
    print("Current content dictionary contains:", len(generator.CONTENT_DICT), "characters")
    print("Special shape symbols:")
    print("  Solid circle: 'circle'")
    print("  Hollow circle: 'circle_hollow'")
    print("  Solid square: 'square'") 
    print("  Hollow square: 'square_hollow'")
    print("=" * 50)
    # Let user input quantities for each question type
    question_counts = {}
    
    print("\nPlease enter the quantity for each question type:")
    print("Same cube types:")
    question_counts['same_0_faces'] = int(input("  Quantity with 0 same faces: "))
    question_counts['same_1_faces'] = int(input("  Quantity with 1 same face: "))
    question_counts['same_2_faces'] = int(input("  Quantity with 2 same faces: "))
    question_counts['same_3_faces'] = int(input("  Quantity with 3 same faces: "))
    
    print("Different cube types:")
    question_counts['different_content'] = int(input("  Quantity with different content: "))
    question_counts['different_rotation'] = int(input("  Quantity with rotation only difference: "))
    
    total = sum(question_counts.values())
    print(f"\nTotal {total} questions will be generated")
    
    if total > 0:
        generator.generate_questions(question_counts)
    else:
        print("No questions to generate")

if __name__ == "__main__":
    main()
