import os


current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(os.path.dirname(current_file_path))
print(current_directory + "\\pipeline_mise_a_jour.py")