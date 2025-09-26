#!/bin/bash

# Create a directory
mkdir -p my_directory

# Create a file within that directory
echo "This is a sample file." > my_directory/sample_file.txt

# Display the contents of the file
echo "Contents of sample_file.txt:"
cat my_directory/sample_file.txt

# Create a symbolic link to the file
ln -s my_directory/sample_file.txt my_directory/symlink_to_sample_file.txt

# Create a hard link to the file
ln my_directory/sample_file.txt my_directory/hardlink_to_sample_file.txt

# Display the contents of the directory
echo "Contents of my_directory:"
ls -l my_directory

# Display the symbolic and hard link
echo "Symlink and Hardlink details:"
ls -l my_directory/symlink_to_sample_file.txt my_directory/hardlink_to_sample_file.txt
