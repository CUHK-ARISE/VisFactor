import random
import json
import os
import cv2
from tmo import draw_cube

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
        print(f"Debug: FACE_MAPPING length = {len(self.FACE_MAPPING)}")  # Debug info
        print(f"Debug: Looking for key ({front_face_num}, {front_rotation})")  # Debug info
        
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
                print(f"Found mapping: up=Face{up_face_num}({up_rotation}°), right=Face{right_face_num}({right_rotation}°)")
            else:
                print(f"Warning: Mapping not found for ({front_face_num}, {front_rotation})")
                print(f"Available keys: {list(self.FACE_MAPPING.keys())[:5]}...")  # Show first 5 keys
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
    
    def generate_same_question(self, question_num):
        """Generate Same type question: two identical cubes with different viewing angles"""
        # Create one cube
        cube_faces = self.create_cube_faces()
        
        # Randomly select two different display configurations
        available_configs = list(self.FACE_MAPPING.keys())
        if len(available_configs) < 2:
            print("Warning: Insufficient mapping configurations, using random configuration")
            front_face_1 = random.randint(1, 6)
            front_rotation_1 = random.choice(self.ROTATIONS)
            front_face_2 = random.randint(1, 6)
            front_rotation_2 = random.choice(self.ROTATIONS)
        else:
            config_1 = random.choice(available_configs)
            config_2 = random.choice([c for c in available_configs if c != config_1])
            front_face_1, front_rotation_1 = config_1
            front_face_2, front_rotation_2 = config_2
        
        # Get visible faces for both display configurations
        visible_1 = self.get_visible_faces(cube_faces, front_face_1, front_rotation_1)
        visible_2 = self.get_visible_faces(cube_faces, front_face_2, front_rotation_2)
        
        # Generate images
        self.generate_cube_image(visible_1, f"{question_num}-0.jpg")
        self.generate_cube_image(visible_2, f"{question_num}-1.jpg")
        
        return "Same", cube_faces, visible_1, visible_2
    
    def generate_different_question(self, question_num):
        """Generate Different type question: second cube has one different face"""
        # Create the first cube
        cube_faces_1 = self.create_cube_faces()
        front_face_1 = random.randint(1, 6)
        front_rotation_1 = random.choice(self.ROTATIONS)
        visible_1 = self.get_visible_faces(cube_faces_1, front_face_1, front_rotation_1)
        
        # Get the 6 contents used by the first cube
        used_contents = [cube_faces_1[i]['content'] for i in range(1, 7)]
        
        # Randomly redistribute these 6 contents to the second cube's 6 faces
        shuffled_contents = used_contents.copy()
        random.shuffle(shuffled_contents)
        
        cube_faces_2 = {}
        for i in range(1, 7):
            cube_faces_2[i] = {
                'content': shuffled_contents[i-1],
                'rotation': random.choice(self.ROTATIONS)
            }
        
        # Randomly select one face to change to new content
        face_to_change = random.randint(1, 6)
        available_contents = [c for c in self.CONTENT_DICT if c not in used_contents]
        
        if available_contents:
            cube_faces_2[face_to_change]['content'] = random.choice(available_contents)
            cube_faces_2[face_to_change]['rotation'] = random.choice(self.ROTATIONS)
        else:
            print("Warning: No available new content to create Different type question")
        
        # Select display configuration for the second cube
        front_face_2 = random.randint(1, 6)
        front_rotation_2 = random.choice(self.ROTATIONS)
        visible_2 = self.get_visible_faces(cube_faces_2, front_face_2, front_rotation_2)
        
        # Generate images
        self.generate_cube_image(visible_1, f"{question_num}-0.jpg")
        self.generate_cube_image(visible_2, f"{question_num}-1.jpg")
        
        return "Different", cube_faces_1, visible_1, visible_2
    
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
    
    def generate_questions(self, num_questions, same_ratio=0.5):
        """Generate specified number of questions"""
        questions = []
        answers = []
        
        # Calculate number of Same and Different questions
        num_same = int(num_questions * same_ratio)
        num_different = num_questions - num_same
        
        # Create question type list and shuffle
        question_types = ['Same'] * num_same + ['Different'] * num_different
        random.shuffle(question_types)
        
        for i, q_type in enumerate(question_types, 1):
            print(f"Generating question {i}/{num_questions} - Type: {q_type}")
            
            if q_type == 'Same':
                answer, cube1, visible1, visible2 = self.generate_same_question(i)
            else:
                answer, cube1, visible1, visible2 = self.generate_different_question(i)
            
            questions.append([f"./Images/{i}-0.jpg", f"./Images/{i}-1.jpg"])
            answers.append([answer])
        
        # Save to JSON file
        result = {
            "Questions": questions,
            "Answers": answers
        }
        
        with open(os.path.join(self.output_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\nGeneration completed!")
        print(f"Total questions: {num_questions}")
        print(f"Same type: {num_same}")
        print(f"Different type: {num_different}")
        print(f"Files saved in: {self.output_dir}/")

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
    
    # Display mapping summary
    generator.display_mapping_summary()
    
    # Generate questions
    num_questions = int(input("Please enter the number of questions to generate: "))
    same_ratio = float(input("Please enter the ratio of Same type questions (0-1): "))
    
    generator.generate_questions(num_questions, same_ratio)

if __name__ == "__main__":
    main()
