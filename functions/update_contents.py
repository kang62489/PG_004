## Author: Kang
## Last Update: 2025-Feb-02
## Purpose: import the updated rec_summary and then append the updated metadata to the comment of each recording file

list_of_contents_to_be_updated = []
def contentUpdater(new_rec_summary, list_of_kept_contents):
    for data, content in zip(new_rec_summary.iterrows(), list_of_kept_contents):
        properties = data[1].index.tolist()
        for prop in properties[2:]:
            content.append(f"{prop}: {data[1][prop]}")
        list_of_contents_to_be_updated.append(content)
    return list_of_contents_to_be_updated