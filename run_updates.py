import os
import sys
import dotenv

dotenv.load_dotenv()

root = os.path.dirname(os.path.abspath(__file__))
from h3_utils.print_utils import PrintUtils as pu
from h3_utils.launch_args import LAUNCH_ARGS
sys.path.append(root)
os.chdir(root)

if LAUNCH_ARGS.should_check_for_updates:
    try:
        import pygit2
        pygit2.option(pygit2.GIT_OPT_SET_OWNER_VALIDATION, 0)

        repo = pygit2.Repository(os.path.abspath(os.path.dirname(__file__)))

        branch_name = repo.head.shorthand

        remote_name = 'origin'
        remote = repo.remotes[remote_name]

        diff = False

        # Check if the remote branch is ahead of the local branch
        remote_to_check = 'main'
        local_to_check = 'main'
        remote_ref = f'refs/remotes/{remote_name}/{remote_to_check}'
        local_ref = f'refs/heads/{local_to_check}'
        remote_commit = repo.revparse_single(remote_ref)
        local_commit = repo.revparse_single(local_ref)
        if remote_commit.id != local_commit.id:
            diff = True

        user_wants_to_update = False
        if diff:
            if input("The remote branch is ahead of the local branch. Do you want to update? (y/n): ") != 'y':
                user_wants_to_update = True
                remote.fetch()

        if user_wants_to_update:
            local_branch_ref = f'refs/heads/{branch_name}'
            local_branch = repo.lookup_reference(local_branch_ref)

            remote_reference = f'refs/remotes/{remote_name}/{branch_name}'
            remote_commit = repo.revparse_single(remote_reference)

            merge_result, _ = repo.merge_analysis(remote_commit.id)

            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                pu.contprint("Already up-to-date")
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                local_branch.set_target(remote_commit.id)
                repo.head.set_target(remote_commit.id)
                repo.checkout_tree(repo.get(remote_commit.id))
                repo.reset(local_branch.target, pygit2.GIT_RESET_HARD)
                pu.contprint("Fast-forward merge")
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                pu.p_red("Update failed - Did you modify any file?")

            pu.p_green('Update succeeded.')
    except Exception as e:
        pu.p_red('Update failed.')
        pu.p_red(str(e))
else:
    pu.contprint("Skipping update check because should_check_for_updates is False")
