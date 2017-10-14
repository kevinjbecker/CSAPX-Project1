from sys import argv


def main():
    """
        This is the main function of the program. It makes sure that the file has correct arguments or else it won't
        run. Handles the main distribution of the file names too.

        :return: None
    """
    # to add: prompt for file names if argv no have them
    if len(argv) < 3:
        if len(argv) == 2:
            print("Only one file path specified in program call, assuming that as file 1.")
            file_path_1 = argv[1]
        else:
            file_path_1 = input("Enter path for file 1: ")
        file_path_2 = input("Enter path for file 2: ")
    else:
        file_path_1 = argv[1]
        file_path_2 = argv[2]
    exit_codes = ["Files match.", "Files partially match with above differences.", "Files do not match."]

    # if the files are the same path, it is impossible for them to be different.
    # saving compute time by catching this case.
    if file_path_1 == file_path_2:
        print("Files point to same path.\nFiles match.")
    else:
        file_1_html = read_html_file(file_path_1)
        file_2_html = read_html_file(file_path_2)

        # again saving compute time
        if file_1_html == file_2_html:
            print("Files match.")
        else:
            file_1_stripped = strip_new_lines(file_1_html)
            file_1_line_preserved = replace_new_lines(file_1_html)
            file_2_stripped = strip_new_lines(file_2_html)
            file_2_line_preserved = replace_new_lines(file_2_html)

            # EXIT CODE KEY: 0 = MATCH, 1 = PARTIAL MATCH, 2 = NO MATCH
            exit_code = compare_files(file_1_stripped, file_1_line_preserved, file_2_stripped, file_2_line_preserved)

            print(exit_codes[exit_code])


def compare_files(file_1_stripped: str, file_1_line_preserved: str, file_2_stripped: str, file_2_line_preserved: str)->int:
    """
    Handles the main comparison of the files.

    :param file_1_stripped: The stripped HTML string of file 1. Stripped means there is no extra white space or new line
    characters.
    :param file_1_line_preserved: The stripped HTML string of file 1 with the new lines preserved. (New lines are
    instead saved as a "$")
    :param file_2_stripped:The stripped HTML string of file 2. Stripped means there is no extra white space or new line
    characters.
    :param file_2_line_preserved:The stripped HTML string of file 2 with the new lines preserved. (New lines are
    instead saved as a "$")

    :return: An integer of the type of file comparison achieved. 0 = match, 1 = partial match, 2 = no match.
    """
    if file_1_stripped == file_2_stripped:
        return 0

    file_1_stripped_full = file_1_stripped
    file_2_stripped_full = file_2_stripped

    index_file_1 = 0
    index_file_2 = 0
    mismatches = False

    while len(file_1_stripped) > 0:
        index_file_1 += 1
        index_file_2 += 1
        if len(file_2_stripped) == 0:
            print("Unexpected end of file 2. Aborting operation.")
            return 2
        elif file_1_stripped[0] != file_2_stripped[0]:
            mismatches = True
            # find_and_report_errors will find the errors
            continue_points = find_and_report_errors(file_1_stripped_full, file_1_stripped, file_1_line_preserved, index_file_1,
                                                     file_2_stripped_full, file_2_stripped, file_2_line_preserved, index_file_2)
            if type(continue_points) == bool and not continue_points or continue_points[0] == -1:
                return 2
            else:
                file_1_stripped = file_1_stripped[continue_points[0]:]
                index_file_1 += continue_points[0]
                file_2_stripped = file_2_stripped[continue_points[1]:]
                index_file_2 += continue_points[1]

        file_1_stripped = file_1_stripped[1:]
        file_2_stripped = file_2_stripped[1:]

    if len(file_2_stripped) > 0:
        print("Unexpected end of file 1. Aborting operation.")
        return 2

    return 1 if mismatches else 0


def find_and_report_errors(file_1_full: str, file_1_shortened: str, file_1_lines: str, file_1_error_start_index: int,
                           file_2_full: str, file_2_shortened: str, file_2_lines: str, file_2_error_start_index: int):

    # the eventual return if find_and_report completes; lets the function that calls it know what to remove.
    index_return = []

    file_1_line_number = str(get_line_number(file_1_lines, file_1_error_start_index))
    file_2_line_number = str(get_line_number(file_2_lines, file_2_error_start_index))

    if in_tag(file_1_shortened) or in_tag(file_2_shortened):
        # if we're in a tag, we need to find the tag-mismatch, this does that
        tag_mismatch = get_tag_mismatch(file_1_full, file_1_shortened, file_1_error_start_index, file_2_full,
                                        file_2_shortened, file_2_error_start_index)

        # if the tag mismatch can't be resolved (i.e. tag mismatch at outermost level)
        if tag_mismatch[1] == -1:
            print("On the following lines...\nfile 1: " + file_1_line_number + ". " + tag_mismatch[4] + "\nfile 2: " +
                  file_2_line_number + ". " + tag_mismatch[5] + "\n" + tag_mismatch[4] + " != " + tag_mismatch[5] +
                  ". Tag mismatch at outermost level. Aborting operation.\n")
            return [-1, -1]

        # otherwise we're able to resolve and can tell the user this information
        print("On the following lines...\nfile 1: " + file_1_line_number + ". " + tag_mismatch[4] + "\nfile 2: " +
              file_2_line_number + ". " + tag_mismatch[5] + "\n" + tag_mismatch[4] + " != " + tag_mismatch[5] +
              ". Tag mismatch. Attempting to continue to end of " + tag_mismatch[0] + ". Attempt succeeded.\n")
        return [tag_mismatch[1] - file_1_error_start_index, tag_mismatch[3] - file_2_error_start_index]

    # gets the nearest start tags for both files
    file_1_start_tag = find_previous_open_tag(file_1_full, file_1_error_start_index)
    file_2_start_tag = find_previous_open_tag(file_2_full, file_2_error_start_index)

    # gets the end tag that matches the start tag for both files
    file_1_end_tag = find_matching_close_tag(file_1_full, file_1_error_start_index, file_1_start_tag[0])
    file_2_end_tag = find_matching_close_tag(file_2_full, file_2_error_start_index, file_2_start_tag[0])

    # if there is no end tag in either file that can be found, stop searching and fail
    if file_1_end_tag[1] == -1 or file_2_end_tag[1] == -1:
        # returns true because the diff cannot continue.
        print("Closing tag seek failed. Aborting operation.")
        return False

    # gets the string that contained an error (including parent tag)
    file_1_string_to_compare = file_1_full[file_1_start_tag[1]: file_1_end_tag[2]]
    # find the compare string's location in file_1's shortened string
    index_return.append(file_1_shortened.find(file_1_end_tag[0]) + len(file_1_end_tag[0]))
    # strips the outermost tags of the file 1 string to compare (we don't need it, we already know they match)
    file_1_string_to_compare = file_1_string_to_compare[file_1_string_to_compare.find('>') + 1: file_1_string_to_compare.rfind('<')]

    # same as above but for the second file
    file_2_string_to_compare = file_2_full[file_2_start_tag[1]: file_2_end_tag[2]]
    # perform the same as above for file_2
    index_return.append(file_2_shortened.find(file_2_end_tag[0]) + len(file_2_end_tag[0]))
    # strip the outermost tags of the file 2 string to compare (we don't need it, we already know they match)
    file_2_string_to_compare = file_2_string_to_compare[file_2_string_to_compare.find('>') + 1:file_2_string_to_compare.rfind('<')]

    file_1_string_currently_comparing = ""
    file_2_string_currently_comparing = ""

    while True:
        if len(file_1_string_to_compare) == 0 or len(file_2_string_to_compare) == 0:
            break

        # builds the string until the next tag is found (for text mismatch)
        file_1_string_currently_comparing += build_string_until_tag(file_1_string_to_compare)
        file_1_string_to_compare = file_1_string_to_compare[len(file_1_string_currently_comparing):]

        # builds file 2 string to compare
        file_2_string_currently_comparing += build_string_until_tag(file_2_string_to_compare)
        file_2_string_to_compare = file_2_string_to_compare[len(file_2_string_currently_comparing):]

        # if they don't match, report the error
        if file_1_string_currently_comparing != file_2_string_currently_comparing:
            # if we're not in a tag, we can tell user it is just a text-mismatch
            if "<" not in file_1_string_currently_comparing:
                # have to get the lines here
                print("On the following lines...\nfile 1: " + file_1_line_number + ". " +
                      file_1_full[file_1_start_tag[1]: file_1_end_tag[2]] + "\nfile 2: " + file_2_line_number + ". " +
                      file_2_full[file_2_start_tag[1]: file_2_end_tag[2]] + "\n\"" + file_1_string_currently_comparing +
                      "\" != \"" + file_2_string_currently_comparing + "\". Simple text mismatch. Continuing.\n")

                if len(file_1_string_to_compare) == 0 or len(file_2_string_to_compare) == 0:
                    break

                file_1_string_currently_comparing = file_1_string_to_compare[0]
                file_2_string_currently_comparing = file_2_string_to_compare[0]

                file_1_string_to_compare = file_1_string_to_compare[1:]
                file_2_string_to_compare = file_2_string_to_compare[1:]
            # otherwise it's a tag error within the current tag and we can tell the user this information
            else:
                # else its a tag, compare their innards to make sure they match, otherwise break the compare and
                # alert that there was a tag mismatch
                print("On the following lines...\nfile 1: " + file_1_line_number + ". " +
                      file_1_full[file_1_start_tag[1]: file_1_end_tag[2]] + "\nfile 2: " + file_2_line_number + ". " +
                      file_2_full[file_2_start_tag[1]: file_2_end_tag[2]] + "\n" + file_1_string_currently_comparing +
                      " != " + file_2_string_currently_comparing + ". Tag mismatch. Attempting to continue to end of " +
                      file_1_start_tag[0] + ". Succeeded.\n")
                return index_return

    return index_return


def get_line_number(file_string_with_lines: str, file_error_start_index: int)-> int:
    """

    :param file_string_with_lines:
    :param file_error_start_index:

    :return:
    """
    line_count = 1
    current_string_index = 1
    for index in range(0, len(file_string_with_lines)):
        if file_string_with_lines[index] == "%$":
            line_count += 1
        else:
            current_string_index += 1
            if current_string_index == file_error_start_index:
                return line_count


def in_tag(shortened_string: str)->bool:
    if shortened_string.find(">") < shortened_string.find('<') or ('<' not in shortened_string and '>' in shortened_string):
        return True
    return False


def get_tag_mismatch(file_1_full: str, file_1_shortened: str, file_1_error_start_index: int, file_2_full: str,
                     file_2_shortened: str, file_2_error_start_index: int)->list:
    # gets the string of file 1 starting at the error index (we don't need anything before
    file_1_string_starting_at_index = file_1_full[:file_1_error_start_index + file_1_shortened.find('>')]
    # gets the string of file 2 starting at the error index (we don't need anything before
    file_2_string_starting_at_index = file_2_full[:file_2_error_start_index + file_2_shortened.find('>')]

    # gets the tag from file 1
    file_1_tag = file_1_string_starting_at_index[file_1_string_starting_at_index.rfind('<'):]
    file_2_tag = file_2_string_starting_at_index[file_2_string_starting_at_index.rfind('<'):]

    # gets the parent tags for each file
    file_1_parent_tag = find_parent_tag(file_1_full, file_1_string_starting_at_index)
    file_2_parent_tag = find_parent_tag(file_2_full, file_2_string_starting_at_index)

    return [file_1_parent_tag[0], file_1_parent_tag[1], file_2_parent_tag[0], file_2_parent_tag[1], file_1_tag, file_2_tag]


def find_parent_tag(file_string: str, string_up_to_start_index: str)->list:
    if ">" not in string_up_to_start_index:
        return [file_string[file_string.find("<"): file_string.find(">")+1], -1]

    if string_up_to_start_index.rfind("<") > string_up_to_start_index.rfind(">"):
        string_up_to_start_index = string_up_to_start_index[:string_up_to_start_index.rfind(">")+1]

    second_tag_start_index = string_up_to_start_index.rfind("<")
    second_tag_end_index = string_up_to_start_index.rfind(">")
    second_tag = string_up_to_start_index[second_tag_start_index:second_tag_end_index+1]

    while True:
        first_tag_start_index = string_up_to_start_index[:second_tag_start_index].rfind("<")
        first_tag_end_index = string_up_to_start_index[:second_tag_end_index].rfind(">")
        first_tag = string_up_to_start_index[first_tag_start_index:first_tag_end_index+1]

        if "/" not in first_tag and "/" not in second_tag and second_tag_start_index - first_tag_end_index == 1:
            if first_tag_start_index == 0:
                return [first_tag, len(file_string)]

            continue_searching_from_index = find_matching_close_tag(file_string, first_tag_end_index+1, first_tag)

            return [first_tag, continue_searching_from_index[2]]

        second_tag_start_index = first_tag_start_index
        second_tag_end_index = first_tag_end_index
        second_tag = first_tag


def build_string_until_tag(string_to_build_from: str)-> str:
    """
    Builds a string that is in between two tag markers (can be a tag or just a text string).

    :param string_to_build_from: The string that should be used to build the string until tag.

    :return: The string that appears between the two tag markers.
    """
    # The built string that will be returned
    built_string = ""

    # though it may seem like this is excess, it is needed since two items are being compared simultaneously
    # this is the fastest way to do it
    while len(string_to_build_from) > 0 and string_to_build_from[0] != "<":
        built_string += string_to_build_from[0]
        string_to_build_from = string_to_build_from[1:]

    # once we have built the string we can return it
    return built_string


def find_previous_open_tag(full_string: str, start_search_index: int)->list:
    """
    Used to find the previous tag before the error had been reached.

    :param full_string: The full string of the HTML file.
    :param start_search_index: The index to begin searching back from.

    :return: A list containing the previous open tag that appears before start_search_index, the beginning index of that
    tag and the end index of the tag.
    """

    # chops the string so that we don't have anything after the start index (we don't need it)
    string_up_to_start_index = full_string[:start_search_index]

    # if we end on an open tag, that is an issue so we remove one character
    if string_up_to_start_index[-1] == "<":
        string_up_to_start_index = string_up_to_start_index[:-1]
    # if the string ends on a tag we go forward one character just to be safe
    elif string_up_to_start_index[-1] == ">":
        string_up_to_start_index += full_string[:start_search_index+1]

    # the current tag's start index is found
    current_tag_start_index = string_up_to_start_index.rfind("<")

    # the current tag's end index is found
    current_tag_end_index = string_up_to_start_index.rfind(">")

    # we need to keep looping until we get a solution so we just create this infinite loop
    while True:
        # gets the tag
        tag = full_string[current_tag_start_index: current_tag_end_index+1]
        # if it isn't a close tag, we have arrived at the point we want to be at
        if "/" not in tag:
            return [tag, current_tag_start_index, current_tag_end_index+1]
        # otherwise we keep searching by resetting the string, and getting the next tag
        string_up_to_start_index = string_up_to_start_index[:current_tag_start_index]
        current_tag_start_index = string_up_to_start_index.rfind("<")
        current_tag_end_index = string_up_to_start_index.rfind(">")


def find_matching_close_tag(file_string: str, start_search_index: int, tag_to_match: str)->list:
    """
    Finds the matching close tag, starting from start_search_index that matches tag_to_match

    :param file_string: The entire file_string that is to be searched.
    :param start_search_index: The index of file_string that the search should begin from.
    :param tag_to_match: The tag that is to be matched.

    :return: A list containing tag, the index to begin the search from, and its end index.
    """

    # removes the beginning part of the string since we don't need that (we subtract one just in case the
    # string starts at a tag
    string_starting_at_index = file_string[start_search_index-1:]
    # the final start index is the start_search_index-1
    final_start_index = start_search_index-1
    # the number of close tags remaining is 1 (this is used in case we find other open tags, we need to keep track
    # of how many that we have to find before we can return
    close_tags_remaining = 1

    # if the string has a ">" before a "<", that is an issue and we need to resolve that as done here
    if string_starting_at_index.find("<") > string_starting_at_index.find(">"):
        final_start_index += string_starting_at_index.find("<")
        string_starting_at_index = string_starting_at_index[string_starting_at_index.find("<"):]

    # the index of the first tag
    current_tag_start_index = string_starting_at_index.find("<")
    # the final index in the original string can be updated to be the index
    # this is because we its location is index away from the start_index
    final_start_index += current_tag_start_index

    # the end index of the tag can now be found
    current_tag_end_index = string_starting_at_index.find(">")

    # this loop needs to go forever until we get an answer
    while True:
        # if the index can't be found (i.e. returns -1)
        if current_tag_end_index == -1:
            return ["", -1, -1]

        # the actual tag is found here
        tag = string_starting_at_index[current_tag_start_index: current_tag_end_index+1]
        # the final start of the index is updated to be the length of the tag
        final_start_index += len(tag)

        # if we find another open tag that matches the requested we need to go until we find enough close tags
        if tag == tag_to_match:
            close_tags_remaining += 1
        # else if we get a close tag and it matches the tag we are seeking
        elif tag.replace("/", "") == tag_to_match:
            # subtract one from the remaining close tags
            close_tags_remaining -= 1
            # if we've reached enough close tags, we can now return since we've hit our desired point
            if close_tags_remaining == 0:
                final_start_index -= len(tag)
                return [tag, final_start_index, final_start_index + len(tag)]

        # if we get to this point, it sets us up for the next tag performing similar actions before the loop
        string_starting_at_index = string_starting_at_index[current_tag_end_index + 1:]
        current_tag_start_index = string_starting_at_index.find("<")
        current_tag_end_index = string_starting_at_index.find(">")
        final_start_index += current_tag_start_index


def read_html_file(html_file_path: str)->str:
    """
    Reads in an HTML file and returns it as a single string.

    :param html_file_path: The path to the HTML file.

    :return: The read in HTML file as a single string.
    """

    # makes a blank string that we will eventually return
    html_file_string = ""

    # opens the file and keeps it open
    with open(html_file_path) as file:
        # goes through each lines
        for line in file:
            html_file_string += line

    # return the read in file
    return html_file_string


def strip_white_space(html_string: str)->str:
    """
    Strips any excess whitespace from the HTML (usually around the tags)

    :param html_string: The html_string to have the new line characters removed from

    :return: The new string with no excess whitespace
    """

    return " ".join(html_string.split()).replace("> <", "><").replace("> ", ">").replace(" <", "<")\
        .replace(">%$ ", ">%$").replace(" %$<", "%$<")


def strip_new_lines(html_string: str)->str:
    """
    Strips all of the new line characters from html_string.

    :param html_string: The html_string to have the new line characters removed from

    :return: The new string with no new line characters
    """
    return strip_white_space(html_string.replace("\n", ""))


def replace_new_lines(html_string: str)->str:
    """
    Replaces the new line characters with a "%$" string. This is used to determine line number later on in the process.

    :param html_string: The html_string to have the new line characters replaced

    :return: The new string with no new line characters and a "%$" in its place
    """
    return strip_white_space(html_string.replace("\n", "%$"))


if __name__ == '__main__':
    if len(argv) > 3:
        print("Illegal number of arguments used.\nUsage: $python3 html_compare.py [file1, file2]")
    else:
        main()
