import json
import os
import cv2
from DrawCube import draw_cube

class CubeRestorer:
    def __init__(self, images_dir="Images"):
        self.images_dir = images_dir
        self.ROTATIONS = [0, 90, 180, 270]
        
        # Cube face mapping table - same as in Gen.py
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
    def load_question_data(self, question_num):
        """Load data for specified question"""
        data_file = os.path.join(self.images_dir, f"question_{question_num}_data.json")
        
        if not os.path.exists(data_file):
            print(f"Data file does not exist: {data_file}")
            return None
        
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def display_cube_info(self, cube_faces, cube_name="Cube"):
        """Display complete information of cube"""
        print(f"\n{cube_name} Complete Information:")
        print("-" * 40)
        for face_num in range(1, 7):
            face_data = cube_faces[str(face_num)]
            print(f"  Face {face_num}: {face_data['content']} (rotation {face_data['rotation']}°)")
    
    def display_visible_faces_info(self, view_data, view_name="View"):
        """Display information of visible faces"""
        print(f"\n{view_name} Visible Face Information:")
        print("-" * 40)
        config = view_data['config']
        visible = view_data['visible_faces']
        
        print(f"Observation config: front={config[0]}, front_rotation={config[1]}°")
        print("Visible faces:")
        for position in ['front', 'up', 'right']:
            face_info = visible[position]
            print(f"  {position:>5}: Face{face_info['face_num']} - {face_info['content']} (rotation {face_info['rotation']}°)")
    
    def generate_all_views_for_cube(self, cube_faces, output_prefix):
        """Generate all possible views for a cube"""
        print(f"\nGenerating all views for {output_prefix}...")
        
        view_count = 0
        for config in self.FACE_MAPPING.keys():
            front_face, front_rotation = config
            
            # Calculate visible faces
            visible_faces = self.get_visible_faces(cube_faces, front_face, front_rotation)
            
            # Generate image
            filename = f"{output_prefix}_view_{view_count:02d}_F{front_face}R{front_rotation}.jpg"
            self.generate_cube_image(visible_faces, filename)
            
            view_count += 1
        
        print(f"Generated {view_count} views")
    def get_visible_faces(self, cube_faces, front_face_num, front_rotation):
        """Get visible face information based on front face number and rotation angle"""
        if (front_face_num, front_rotation) in self.FACE_MAPPING:
            up_face_num, up_rotation, right_face_num, right_rotation = self.FACE_MAPPING[(front_face_num, front_rotation)]
        else:
            print(f"Warning: Mapping not found for ({front_face_num}, {front_rotation})")
            return None
        
        # Get actual face content and rotation angles
        front_content = cube_faces[str(front_face_num)]['content']
        front_rot = (cube_faces[str(front_face_num)]['rotation'] + front_rotation) % 360
        
        up_content = cube_faces[str(up_face_num)]['content']
        up_rot = (cube_faces[str(up_face_num)]['rotation'] + up_rotation) % 360
        
        right_content = cube_faces[str(right_face_num)]['content']
        right_rot = (cube_faces[str(right_face_num)]['rotation'] + right_rotation) % 360
        
        return {
            'front': {'content': front_content, 'rotation': front_rot, 'face_num': front_face_num},
            'up': {'content': up_content, 'rotation': up_rot, 'face_num': up_face_num},
            'right': {'content': right_content, 'rotation': right_rot, 'face_num': right_face_num}
        }
    
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
        
        # Create restore output directory
        restore_dir = os.path.join(self.images_dir, "restored_views")
        if not os.path.exists(restore_dir):
            os.makedirs(restore_dir)
        
        filepath = os.path.join(restore_dir, filename)
        cv2.imwrite(filepath, cube_img)
    def restore_question(self, question_num):
        """Restore cube for specified question"""
        data = self.load_question_data(question_num)
        
        if data is None:
            return
        
        print(f"\n" + "=" * 60)
        print(f"Question {question_num} Restoration Information")
        print("=" * 60)
        print(f"Question type: {data['question_type']}")
        
        if data['question_type'] == 'Same':
            print(f"Target same face count: {data['target_same_count']}")
            print(f"Actual same face count: {data['same_face_count']}")
            
            # Display cube information
            self.display_cube_info(data['cube_faces'], "Original Cube")
            
            # Display information for two views
            self.display_visible_faces_info(data['view_1'], "View 1")
            self.display_visible_faces_info(data['view_2'], "View 2")
            
            # Generate all views
            self.generate_all_views_for_cube(data['cube_faces'], f"Q{question_num}_cube")
        
        elif data['question_type'].startswith('Different'):
            # Display information for two different cubes
            self.display_cube_info(data['cube_faces_1'], "Cube 1")
            self.display_cube_info(data['cube_faces_2'], "Cube 2")
            
            # Display view information
            self.display_visible_faces_info(data['view_1'], "Cube 1 View")
            self.display_visible_faces_info(data['view_2'], "Cube 2 View")
            
            # Generate all views
            self.generate_all_views_for_cube(data['cube_faces_1'], f"Q{question_num}_cube1")
            self.generate_all_views_for_cube(data['cube_faces_2'], f"Q{question_num}_cube2")
    
    def restore_all_questions(self):
        """Restore cubes for all questions"""
        question_files = [f for f in os.listdir(self.images_dir) if f.startswith("question_") and f.endswith("_data.json")]
        
        if not question_files:
            print("No question data files found")
            return
        
        question_nums = []
        for filename in question_files:
            try:
                num = int(filename.split("_")[1])
                question_nums.append(num)
            except:
                continue
        
        question_nums.sort()
        
        print(f"Found data files for {len(question_nums)} questions")
        
        for num in question_nums:
            self.restore_question(num)
    
    def list_questions(self):
        """List all available questions"""
        question_files = [f for f in os.listdir(self.images_dir) if f.startswith("question_") and f.endswith("_data.json")]
        
        if not question_files:
            print("No question data files found")
            return []
        
        question_nums = []
        for filename in question_files:
            try:
                num = int(filename.split("_")[1])
                question_nums.append(num)
            except:
                continue
        
        question_nums.sort()
        
        print(f"\nAvailable question numbers: {question_nums}")
        return question_nums

def main():
    restorer = CubeRestorer()
    
    print("Cube Restoration Tool")
    print("=" * 50)
    
    available_questions = restorer.list_questions()
    
    if not available_questions:
        return
    
    while True:
        print("\nOptions:")
        print("1. Restore specific question")
        print("2. Restore all questions")
        print("3. List all questions")
        print("4. Exit")
        
        choice = input("\nPlease select (1-4): ").strip()
        
        if choice == "1":
            try:
                question_num = int(input("Please enter question number: "))
                if question_num in available_questions:
                    restorer.restore_question(question_num)
                else:
                    print(f"Question {question_num} does not exist")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == "2":
            restorer.restore_all_questions()
        
        elif choice == "3":
            restorer.list_questions()
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid selection, please try again")

if __name__ == "__main__":
    main()