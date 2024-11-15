import looker_sdk
import hashlib
import argparse
import os
import sys

sdk = looker_sdk.init40()

def parse_broken_content(base_url, broken_content, folder_data):
    """Parse and return relevant data from content validator"""
    output = []
    for item in broken_content:
        if item.dashboard:
            content_type = "dashboard"
        else:
            content_type = "look"
        item_content_type = getattr(item, content_type)
        id = item_content_type.id
        name = item_content_type.title
        folder_id = item_content_type.folder.id
        folder_name = item_content_type.folder.name
        errors = item.errors
        url = f"{base_url}/{content_type}s/{id}"
        folder_url = "{}/folders/{}".format(base_url, folder_id)
        if content_type == "look":
            element = None
        else:
            dashboard_element = item.dashboard_element
            element = dashboard_element.title if dashboard_element else None
        # Lookup additional folder information
        folder = next(i for i in folder_data if str(i.id) == str(folder_id))
        parent_folder_id = folder.parent_id
        if parent_folder_id is None or parent_folder_id == "None":
            parent_folder_url = None
            parent_folder_name = None
        else:
            parent_folder_url = "{}/folders/{}".format(base_url, parent_folder_id)
            parent_folder = next(
                (i for i in folder_data if str(i.id) == str(parent_folder_id)), None
            )
            # Handling an edge case where folder has no name. This can happen
            # when users are improperly generated with the API
            try:
                parent_folder_name = parent_folder.name
            except AttributeError:
                parent_folder_name = None
        # Create a unique hash for each record. This is used to compare
        # results across content validator runs
        unique_id = hashlib.md5(
            "-".join(
                [str(id), str(element), str(name), str(errors), str(folder_id)]
            ).encode()
        ).hexdigest()
        data = {
            "unique_id": unique_id,
            "content_type": content_type,
            "name": name,
            "url": url,
            "dashboard_element": element,
            "folder_name": folder_name,
            "folder_url": folder_url,
            "parent_folder_name": parent_folder_name,
            "parent_folder_url": parent_folder_url,
            "errors": str(errors),
        }
        output.append(data)
    return output

def compare_broken_content(broken_content_prod, broken_content_dev):
    """Compare output between 2 content_validation runs"""
    unique_ids_prod = set([i["unique_id"] for i in broken_content_prod])
    unique_ids_dev = set([i["unique_id"] for i in broken_content_dev])
    new_broken_content_ids = unique_ids_dev.difference(unique_ids_prod)
    new_broken_content = []
    for item in broken_content_dev:
        if item["unique_id"] in new_broken_content_ids:
            new_broken_content.append(item)
    return new_broken_content

def checkout_dev_branch(branch, project):
    """Enter dev workspace"""
    sdk.update_session(looker_sdk.models40.WriteApiSession(workspace_id="dev"))
    """Update git branch"""
    sdk.update_git_branch(project_id=project, body=looker_sdk.models40.WriteGitBranch(name=branch))
    """Pull remote changes"""
    sdk.reset_project_to_remote(project_id=project)

def main(branch, project):
    """Compare the output of content validator runs
    in production and development mode.
    Use this script to test whether LookML changes
    will result in new broken content."""
    base_url_data = os.getenv("LOOKERSDK_BASE_URL")
    print("Checking for broken content in production.")
    prod_broken_content_data = sdk.content_validation().content_with_errors
    prod_folders_data = sdk.all_folders(fields="id, parent_id, name")
    broken_content_prod = parse_broken_content(
        base_url_data, prod_broken_content_data, prod_folders_data
    )
    checkout_dev_branch(branch, project)
    print("Checking for broken content in dev branch.")
    dev_broken_content_data = sdk.content_validation().content_with_errors
    dev_folders_data = sdk.all_folders(fields="id, parent_id, name")
    broken_content_dev = parse_broken_content(
        base_url_data, dev_broken_content_data, dev_folders_data
    )
    print("Comparing broken content from prod and dev.")
    new_broken_content = compare_broken_content(broken_content_prod, broken_content_dev)
    if new_broken_content:
        print(new_broken_content)
        print("Ninja's warning 🐱‍👤: New broken content detected. Kindly, fix the content validator.")
        sys.exit(1)  # Exit with non-zero code indicating failure
    else:
        print("Ninja's Warning 🐱‍👤: You are the best 🐱‍🏍! No new broken content in development branch. ")
        sys.exit(0)  # Exit with zero code indicating success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run content validator')
    parser.add_argument('--branch', '-b', type=str,
                        help='Name of branch you want to validate. If omitted, this will use prod.')
    parser.add_argument('--project', '-p', type=str,
                        help='Name of project to validate. This arg is required.')
    args = parser.parse_args()
    main(args.branch, args.project)