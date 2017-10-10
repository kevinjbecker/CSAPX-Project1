from sys import argv


def main():
    file_path_1 = argv[1]
    file_path_2 = argv[2]

    # if the files are the same path, it is impossible for them to be different.
    # saving compute time by catching this case.
    if file_path_1 == file_path_2:
        print("Files point to same directory. Files match.")
    else:
        file_1_html = read_html_files(file_path_1)
        file_2_html = read_html_files(file_path_2)

        # again saving compute time
        if file_1_html == file_2_html:
            print("Files match.")
        else:
            diff = html_split(file_path_1, file_path_2)
            print(diff)


def read_html_files(file_path: str)->list:
    html_file_return = []
    with open(file_path) as file:
        for line in file:
            html_file_return.append(line)
    return html_file_return


def html_split(html_contents_1: str, html_contents_2: str)->str:
    pass


def compare_html(html_string_1: str, htlm_string_2: str)->str:
    pass


if __name__ == '__main__':
    main()
