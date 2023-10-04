import sys
from arg_parser import get_args
from fast_structures import FASTASequenceHandler, FASTQSequenceHandler


def main():
    args = get_args()
    
    # Map extensions to handlers
    handler_map = {
        'fasta': FASTASequenceHandler,
        'fastq': FASTQSequenceHandler
    }

    # Retrieve the appropriate handler based on file extension
    _, input_ext = args.input.rsplit('.', 1)
    handler = handler_map.get(input_ext)
    
    # Argument mappings for operations
    operation_args_map = {
        'trim': ('trim_right', 'trim_left'),
        'adaptor-removal': ('adaptor',)
    }
    
    # Retrieve the required argument names for the operation
    operation_args = operation_args_map.get(args.operation, ())

    print(f"Performing {args.operation} to input file {args.input}.")

    # Execute the operation by passing relevant arguments dynamically
    if '-' in args.operation:
        args.operation = args.operation.replace('-', '_')

    handler.process_file(
        args.input,
        args.output,
        args.operation,
        *[item for arg_name in operation_args for item in (arg_name, getattr(args, arg_name))]
    )

if __name__ == "__main__":
    main()
