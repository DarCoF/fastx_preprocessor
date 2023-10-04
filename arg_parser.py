import argparse
import sys

def valid_file_format(file_name, formats):
    _, ext = file_name.rsplit('.', 1)
    if ext not in formats:
        raise argparse.ArgumentTypeError(f"File must be of format: {', '.join(formats)}")
    return file_name

def valid_operation_type(op_type, valid_ops):
    if op_type not in valid_ops:
        raise argparse.ArgumentTypeError(f"Invalid operation. Must be one of: {', '.join(valid_ops)}")
    return op_type

def positive_integer(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue

def validate_nucleotides(s):
    valid_chars = set("ATCGN")
    if not all(char in valid_chars for char in s):
        raise argparse.ArgumentTypeError('Invalid string. String can only contain [A, T, C, G, N].')
    return s

def get_args():
    parser = argparse.ArgumentParser(description="Process .fasta or .fastq files.")
    valid_file_formats = ['fasta', 'fastq']
    valid_operations = ['rc', 'trim', 'adaptor-removal']

    parser.add_argument("--input",
                        required=True,
                        type=lambda fn: valid_file_format(fn, valid_file_formats),
                        help="Input file, must be of format .fasta or .fastq")

    parser.add_argument("--output",
                        required=True,
                        type=lambda fn: valid_file_format(fn, valid_file_formats),
                        help="Output file, must be of format .fasta or .fastq")

    parser.add_argument("--operation",
                        required=True,
                        type=lambda op: valid_operation_type(op, valid_operations),
                        help="Operation to perform. Must be one of [rc, trim, adaptor-removal]")
    
    parser.add_argument("--trim-right",
                    required=False,
                    type=positive_integer,
                    help="Number of characters to trim at sequence end. Must be a positive integer.")
    
    parser.add_argument("--trim-left",
                    required=False,
                    type=positive_integer,
                    help="Number of characters to trim at sequence start. Must be a positive integer.")
    
    parser.add_argument("--adaptor",
                    required=False,
                    type=lambda ad: validate_nucleotides(ad),
                    help="Pattern to search and remove at beginning of sequence. Must be exclusively made up of characters in [A, T, C, G, N]")
    
    # Parse arguments before further validation
    args = parser.parse_args()
    
    # Ensure input and output are of the same format
    _, input_ext = args.input.rsplit('.', 1)
    _, output_ext = args.output.rsplit('.', 1) 
  
    if input_ext != output_ext:
        print("Error: Input and output files must be of the same format.", file=sys.stderr)
        sys.exit(1)

    # Ensure operation parameters are input based on operation type.
    if args.operation == 'trim':
        if args.trim_right is None or args.trim_left is None:
            parser.error("When --operation is 'trim', --trim-right and --trim-left are required.")

    if args.operation == 'adaptor-removal':
        if args.adaptor is None:
            parser.error("When --operation is 'adaptor-removal', --adaptor is required.")

    return args
