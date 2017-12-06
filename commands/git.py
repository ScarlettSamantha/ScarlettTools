from glob import glob
import os
import git

class Git():
    @classmethod
    def massupdate(cls):
        for dir in glob(os.path.abspath(os.getcwd()) + '/*'):
            # Has to be dir and contain a .git folder.
            if os.path.isdir(dir) == False or os.path.exists(os.path.abspath(dir) + '/.git') == False:
                continue
            try:
                cGitRepo = git.Repo(dir + '/')
                if cGitRepo.remotes is not None:
                    cGitRepo.remotes[0].fetch()
                cGitRepo.head.reset(index=True, working_tree=True)
            except git.InvalidGitRepositoryError:
                print('%s is not a valid repository' % os.path.abspath(dir))