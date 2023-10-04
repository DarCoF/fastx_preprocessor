import abc
import os
from typing import List
import collections

# COMPLEMENT MAP
COMPLEMENT_BASE = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}

class BaseSequenceHandler(abc.ABC):
    # class variables for statistics
    bases_processed:  dict[str, int] = {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'N': 0}
    sequences: list = [0]
    bases_trimmed: dict[str, int] = {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'N': 0}
    adaptors = list = [0]   

    def __init__(self, sequence):
        self.sequence = sequence

    @staticmethod
    def _update_sequence_counter():
        BaseSequenceHandler.sequences[0] += 1

    def _update_base_counter(self):
        """Count bases in current sequence and update bases_processed"""
        current_base_count = collections.Counter(self.sequence)
        for base, count in current_base_count.items():
            # Ensure the base is expected and present in bases_processed
            if base in BaseSequenceHandler.bases_processed:
                BaseSequenceHandler.bases_processed[base] += count
            else:
                print(f"Warning: Encountered unexpected base {base}.")
    
    def _update_bases_trimmed(self, bases):
        """
        Updates the `bases_trimmed` dictionary with the bases removed during trimming.

        Args:
        - bases (str): Bases that have been trimmed from the sequence.
        """
        trimmed_count = collections.Counter(bases)
        for base, count in trimmed_count.items():
            BaseSequenceHandler.bases_trimmed[base] += count

    @staticmethod
    def _update_adaptors_removed():
        BaseSequenceHandler.adaptors[0] += 1
    
    def _update_sequence_statistics(self):
        """Update class-wide sequence statistics."""
        # Action 1
        self._update_sequence_counter()        
        # Action 2
        self._update_base_counter()

    
    def trim(self, trim_left, trim_right):
        """
        Trims the sequence from both the left and right by specified numbers of characters and 
        updates statistics accordingly.

        Args:
        - trim_left (int): number of bases to trim from the start of the sequence.
        - trim_right (int): number of bases to trim from the end of the sequence.
        """
         # Ensure trim_left and trim_right are positive and not too large
        trim_left = max(0, min(trim_left, len(self.sequence)))
        trim_right = max(0, min(trim_right, len(self.sequence) - trim_left))

        # Track which bases are being trimmed for statistics update
        trimmed_bases_start = self.sequence[:trim_left]
        trimmed_bases_end = self.sequence[-trim_right:] if trim_right > 0 else ''

        # Update the statistics
        self._update_bases_trimmed(bases = trimmed_bases_start + trimmed_bases_end)
        
        # Update the sequence
        self.sequence = self.sequence[trim_left:len(self.sequence)-trim_right]
    
    def rc(self):
        """Generate the reverse complement of the sequence."""
        try:
            self.sequence = "".join(COMPLEMENT_BASE[base] for base in reversed(self.sequence))
        except KeyError as e:
            print(f"Error: Encountered an unexpected base {str(e)} when creating reverse complement.")
    
    def adaptor_removal(self, adaptor):
        """
        Remove the specified adaptor sequence from the start of self.sequence and 
        update statistics accordingly.
        
        Args:
        - adaptor_sequence (str): the sequence to be removed from the start of self.sequence.
        """
        # Check if the sequence starts with the adaptor and remove it if it does
        if self.sequence.startswith(adaptor):
            # Update statistics
            self._update_adaptors_removed()

            self.sequence = self.sequence[len(adaptor):]

    @classmethod
    def process_file(cls, input_filename, output_filename, operation, *operation_args):
        try:
            # Constructing paths
            input_filepath = os.path.join('data', input_filename)
            
            # Check if the 'data' folder and input file exists
            if not os.path.exists('data'):
                raise FileNotFoundError(f"The 'data' folder does not exist.")
            elif not os.path.exists(input_filepath):
                raise FileNotFoundError(f"The file {input_filepath} does not exist.")
            
            # Constructing the output filepath
            output_folder_path = 'result'
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)  # Create 'result' folder if it does not exist
            output_filepath = os.path.join(output_folder_path, output_filename)
            
            # Process the file
            with open(input_filepath, 'r') as infile, open(output_filepath, 'w') as outfile:
                # Prepare operation_args_dict from operation_args tuple
                operation_args_dict = {operation_args[i]: operation_args[i + 1] for i in range(0, len(operation_args), 2)}
                cls._process_file_lines(infile, outfile, operation, **operation_args_dict)

            # Report statistics after processing whole input file
            cls.report_statistics(operation)  
            print(f"File {input_filename} has been successfully {operation}'d. Output stored in file: {output_filename}.")
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    
    @classmethod
    def _process_file_lines(cls, infile, outfile, operation, **operation_args):
        raise NotImplementedError("Subclasses must implement _process_file_lines.")

    @staticmethod
    def _process_single_sequence(seq_class, operation, *args, **operation_args):
        seq_instance = seq_class(*args)
        # Update general statistics
        seq_instance._update_sequence_statistics()
        # Call the operation method with any additional arguments
        getattr(seq_instance, operation)(**operation_args)
        # Convert the modified sequence back and return it
        return str(seq_instance)
    
    @classmethod
    def report_statistics(cls, operation = 'rc'):
        """
        Formats and prints out the statistical information stored in class variables.
        """
        print("---- Sequence Statistics Report ----")
        print(f"Summary:")
        print(f"{cls.sequences[0]:,} reads processed")

        total_bases = sum(cls.bases_processed.values())
        print(f"{total_bases:,} bases processed ", end="")

        if total_bases > 0:
            bases_percentages = {base: (count / total_bases * 100) for base, count in cls.bases_processed.items()}
            bases_report = ", ".join([f"{percentage:.2f}% {base}" for base, percentage in bases_percentages.items()])
            print(f"({bases_report})")
        else:
            print("(No bases processed)")

        if operation == 'trim':
            total_bases_trimmed = sum(cls.bases_trimmed.values())
            print(f"{total_bases_trimmed:,} bases trimmed ", end="")

            if total_bases_trimmed > 0:
                trim_bases_percentages = {base: (count / total_bases_trimmed * 100) for base, count in cls.bases_trimmed.items()}
                trim_bases_report = ", ".join([f"{percentage:.2f}% {base}" for base, percentage in trim_bases_percentages.items()])
                print(f"({trim_bases_report})")
            else:
                print("(No bases processed)")

        if operation == 'adaptor_removal':
            print(f"{cls.adaptors[0]:,} adaptors found")
        
class FASTASequenceHandler(BaseSequenceHandler):
    def __init__(self, header, sequence):
        super().__init__(sequence)
        self.header = header
    
    def __str__(self):
        """Convert FASTA sequence to its string representation."""
        return f"{self.header}\n{self.sequence}\n"

    @classmethod
    def _process_file_lines(cls, infile, outfile, operation, **operation_args):
        header = None
        sequence = []
        for line in infile:
            line = line.strip()
            if line.startswith('>'):
                if header is not None:
                    processed_seq = cls._process_single_sequence(cls, operation, header, ''.join(sequence), **operation_args)
                    outfile.write(processed_seq)
                header = line
                sequence = []
            else:
                sequence.append(line)
        
        if header is not None:
            processed_seq = cls._process_single_sequence(cls, operation, header, ''.join(sequence), **operation_args)
            outfile.write(processed_seq)
    
class FASTQSequenceHandler(BaseSequenceHandler):
    def __init__(self, header, sequence, plus_line, quality_scores):
        super().__init__(sequence)
        self.header = header
        self.plus_line = plus_line
        self.quality_scores = quality_scores    

    def __str__(self):
        """Convert FASTQ sequence to its string representation."""
        return f"{self.header}\n{self.sequence}\n{self.plus_line}\n{self.quality_scores}\n"

    @classmethod
    def _process_file_lines(cls, infile, outfile, operation, **operation_args):
        # Use a generator to group every 4 lines together
        groups = (lines for lines in zip(*[infile] * 4))
        for lines in groups:
            header, sequence, plus_line, quality_scores = map(str.strip, lines)
            outfile.write(cls._process_single_sequence(cls, operation, header, sequence, plus_line, quality_scores, **operation_args))


