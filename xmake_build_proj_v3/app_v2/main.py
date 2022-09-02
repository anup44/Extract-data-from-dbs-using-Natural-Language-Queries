import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("command", type=str, 
                        help="use 'start' to run the app, 'install_models' to install model  files, 'remove_vuln' to  modify vulnerable library")
arg_parser.add_argument('-p', '--port', default=5001,
                        help="port for the app to use")
arg_parser.add_argument("-m", "--models_dir", type=str, default='models', 
                        help="specify the directory where models are stored")

def main():
    args = arg_parser.parse_args()
    if args.command == 'start':
        from query_processor.text_parsing import main
        main()
    
    if args.command == 'install_models':
        from query_processor.install_models import main
        main()

    if args.command == 'remove_vuln':
        from query_processor.change_script import modify_files_rem_vuln
        modify_files_rem_vuln()

    else:
        print ('Not a valid command.')

if __name__ == "__main__":
    main()