#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
from copy import deepcopy
from collections import OrderedDict
from P4 import P4, P4Exception


class Perforce(P4):
    """
    Usage:

    p4 = Perforce()
    with p4.connect():
        p4.checkout()
    """
    def __init__(self, *args, **kwlist):
        super(Perforce, self).__init__(*args, **kwlist)

    def getParentWindow(self):
        """
        App Dependent.

        Returns:
            (QtWidget): Widget to parent to.
        """
        pass

    def getCurrentScene(self):
        """
        App Dependent.

        Returns:
            (string): Path to file to run P4 commands on.
        """
        pass

    def askForPassword(self):
        """
        App Dependent.

        Returns:
            (string): User P4 password.
        """
        pass

    def display(self, text):
        """
        Meant to be overwritten by DCC for custom display options of output.

        Args:
            text (string): Text to display
        """
        print('P4: ' + text)

    @staticmethod
    def _isLatest(file_info):
        """
        Gets whether the given file is on latest revision.

        Args:
            file_info (dictionary): Dictionary from P4 that has all available info about file.

        Returns:
            (boolean): True if is latest, false if not.
        """
        # If user is adding file, then it is latest.
        action = file_info.get('action')
        if action == 'add':
            return True

        head_revision = int(file_info.get('headRev'))
        have_revision = file_info.get('haveRev')

        # if file is deleted and user has it, return False, else True
        head_action = file_info.get('headAction')
        if head_action == 'delete' or head_action == 'move/delete':
            return not bool(have_revision)

        # if user does not have revision, it is not latest.
        if not have_revision:
            return False

        # compare user revision with p4 revision to determine if it is latest.
        return int(have_revision) >= head_revision

    @staticmethod
    def _isInChangelist(file_info):
        """
        Gets whether the given file is in the user's changelist.

        Args:
            file_info (dictionary): Dictionary from P4 that has all available info about file.

        Returns:
            (boolean): True if it is the changelist, false if not.
        """
        return 'action' in file_info

    def _isCheckedOutByOther(self, file_info):
        """
        Gets whether the given file is exclusively checked out by another user.

        Args:
            file_info (dictionary): Dictionary from P4 that has all available info about file.

        Returns:
            (boolean): True if file is exclusively checked out by another user, False if not.
        """
        # if other people have it open for edit AND file is an exclusive check out type
        if 'otherOpens' in file_info and '+l' in file_info['headType']:
            self.display(', '.join(file_info['otherOpen']) + ' has ' + file_info['clientFile'] + ' checked out')
            return True

        return False

    def runChecked(self, *args, **kwargs):
        """
        Checks whether the user is logged in and has a valid ticket before running p4 command.
        If user is not logged in, a PySide2 dialog input will show up prompting for password.

        Returns:
            (Any): Results of command ran.
        """
        try:
            self.run('login', '-s')
        except P4Exception as error_message:

            error_a = 'Your session has expired, please login again.'
            error_b = 'Perforce password (P4PASSWD) invalid or unset.'
            if error_a in self.errors or error_b in self.errors:
                answer = self.askForPassword()

                if not answer:
                    raise error_message

                self.password = answer
                self.run_login()

        return self.run(*args, **kwargs)

    def validatePath(self, path=None):
        """
        Validates the given path by normalizing it and adding necessary characters for directory.

        Args:
            path (string): Path to validate. If None given, will use path defined by self.getCurrentScene().

        Returns:
            (string): Path validated.
        """
        path = path if path else self.getCurrentScene()
        path = os.path.normpath(path)

        # folders required a "/..." to be added for P4 to recognize them as directories
        if os.path.isdir(path):
            path += os.sep + '...'

        return path

    def runPath(self, command, path=None, flags=None):
        """
        Runs the given command through the given path or current scene, with given flags.

        Args:
            command (string): Name of P4 command to run on given path.

            path (Any): Path to run P4 command on. If None given, will use path defined by self.getCurrentScene().

            flags (list): Flags to add AFTER command BEFORE PATH.

        Returns:
            (Any): Results of command ran.
        """
        path = path if path else self.getCurrentScene()

        if not path:
            raise ValueError('No path given, and no path found from current scene!')

        if not isinstance(path, (list, tuple, set, dict)):
            path = [path]

        clients = {}
        for file_path in path:
            file_path = self.validatePath(path=file_path)
            client = self.findClient(file_path, validate_path=False)
            client_file_paths = clients.setdefault(client, [])
            client_file_paths.append(file_path)

        pre_arguments = flags if flags else []
        pre_arguments.insert(0, command)
        output = []

        for client, paths in clients.items():
            if self.client != client:
                self.client = client

            arguments = pre_arguments + paths
            output += self.runChecked(*arguments)

        return output

    def getInfo(self, path=None):
        """
        Gets all the information about the given path in the P4 server.
        Uses the "fstat" command.

        Args:
            path (string or list): Path to get info of. If None given, will use path defined by self.getCurrentScene().

        Returns:
            (list): Each path given contains a dictionary with all the information about each path.
        """
        # setting exception level to 1 to catch and use warnings
        current_level = self.exception_level
        self.exception_level = 1

        info = self.runPath('fstat', path=path)
        for warning in self.warnings:
            info.append({'clientFile': warning.rstrip(' - no such file(s).'), 'notInClient': 1})

        # moving exception back to current level
        self.exception_level = current_level
        return info

    def getServerInfo(self):
        """
        Gets all the information about the P4 server.

        Returns:
            (list): The information about the server. Usually there is one server, so you may only need the first index.
        """
        return self.runChecked('info')

    def getUserClientsInfo(self, user=None):
        """
        Gets all the clients and their information that the given user has.

        Args:
            user (string): Name of user. Usually first letter of first name, and last name, all lowercase.

        Returns:
            (list): Dictionaries of the info of each client.
        """
        return self.runChecked('clients', '-u', user) if user else self.runChecked('clients', '-u', self.user)

    def getUserClientNames(self, user=None):
        """
        Gets all the names of the clients the given user has.

        Args:
            user (string): Name of user. Usually first letter of first name, and last name, all lowercase.

        Returns:
            (list): All the client names given user has.
        """
        clients_info = self.getUserClientsInfo(user=user)
        return [client['client'] for client in clients_info]

    def getDefaultClient(self):
        """
        Gets the default client, the one the user logs in with at the start.

        Returns:
            (string): Name of default client.
        """
        return self.getServerInfo()[0]['clientName']

    def findClient(self, path=None, validate_path=True):
        """
        Finds the client that the given path could be mapped to. Returns FIRST possible client found.
        Sets the currently connected client.
        Will raise error if no client found!

        Args:
            path (string): Path to possible client. If None given, will use path defined by self.getCurrentScene().

            validate_path (boolean): If True, will validate the given path.

        Returns:
            (string): Client that path can map to.
        """
        client_match = None
        path = self.validatePath(path=path) if validate_path else path
        clients = self.getUserClientNames()
        clients.reverse()

        # gross, but will do.
        for client in clients:
            self.client = client

            try:
                client_match = self.run_where(path)
            except Exception:
                pass

            if client_match:
                client_match = client_match[0]['clientFile'].split('/')[2]

                if client_match != client:
                    self.display('Mismatch between found: {} and current: {}'.format(client_match, client))

                return client

        raise P4Exception('No client found to map: ' + path)

    def isInClient(self, path=None, info=None):
        """
        Gets whether the given path is in the current client.

        Args:
            path (string): Path to check if its in client. If None given, will get path with self.getCurrentScene().

            info (list): Information about path to use. If None, will use "fstat" to get info about path.

        Returns:
            (boolean): Wil return info about the given path if is in client, else empty list.
        """
        info = info if info else self.getInfo(path=path)

        for file_info in info:
            if 'notInClient' in file_info:
                return False

        return True

    def getDepots(self, user=None):
        """
        CURRENTLY BROKEN.
        Should get all the mappings associated with a client.

        Args:
            user (string): Name of user to get depots of.

        Returns:
            (dictionary): Depot as key, list of path as first index and client name as second index.
        """
        depots = {}
        computer_name = os.environ['COMPUTERNAME']
        clients = self.getUserClientsInfo(user=user)

        for client in clients:

            # make sure client is on host's computer
            if not user and not client['Host'].upper() == computer_name:
                continue

            # the client doesn't hold the depot path, so we have to use the 'client' command
            client_info = self.run_client('-o', client['client'])[0]

            # the view key holds the depot name, and the optional extra folder mapped to the workspace path
            views = client_info['View'][0].split('...')
            depot_name = views[0]
            extra = views[-2].split(client['client'])[-1]

            if depot_name in depots:
                raise ValueError('More than one ' + depot_name + ' found! Only one depot per workspace supported.')

            # the root key does not contain the full path, so we add the extra
            path = (client['Root'] + extra).replace('\\', '/')
            depots[depot_name] = [path, client['client']]

        return depots

    def isLatest(self, path=None, info=None):
        """
        Gets whether the given path is on latest revision or not. Supports folders!

        Args:
            path (string or list): Path to check whether its latest or not.
            Will use self.getCurrentScene() if no path given.

            info (list): Information about path to use. If None, will use "fstat" to get info about path.

        Returns:
            (boolean): True if given path is latest, else False.
        """
        info = info if info else self.getInfo(path=path)

        for file_info in info:
            if not self._isLatest(file_info):
                return False

        return True

    def getLatest(self, path=None, flags=None, force=False):
        """
        Gets the latest revision of given path.
        Uses "sync" command.

        Args:
            path (string or list): Path to get latest revision of. Will use self.getCurrentScene() if None given.

            flags (list): Extra flags to pass to command.

            force (boolean): If True, will force the revision getting. Even if given path is already on latest.

        Returns:
            (Any): Results of command ran.
        """
        if force:
            flags = flags if flags else []
            flags.append('-f')

        return self.runPath('sync', path=path, flags=flags)

    def isInChangelist(self, path=None, info=None):
        """
        Gets whether the given path(s) are in the changelist.

        Args:
            path (string or list): Path to check if is in changelist. Will use self.getCurrentScene() if None given.

            info (list): Information about path to use. If None, will use "fstat" to get info about path.

        Returns:
            (boolean): True if all file(s) are in changelist, False if just ONE file is NOT in changelist.
        """
        info = info if info else self.getInfo(path=path)

        for file_info in info:
            if not self._isInChangelist(file_info):
                return False

        return True

    def isCheckedOutByOther(self, path=None, info=None, fast_fail=True):
        """
        Gets whether the given path(s) are exclusively checked out by other users or not.

        Args:
            path (string or list): Path to check if is in changelist. Will use self.getCurrentScene() if None given.

            info (list): Information about path to use. If None, will use "fstat" to get info about path.

            fast_fail (bool): If True, will return the file info dict of the first file that is checked out by a user.
            Else will return a list of all the file info dicts that are checked out.

        Returns:
            (list or dictionary): If ANY path(s) given is checked out by another user, will return the file info of the
            path checked out if given fast_fail is set to True. If fast_fail is set to False, will return list of all
            file info paths that are checked out. If no files are checked out, will return empty list.
        """
        info = info if info else self.getInfo(path=path)
        checked_out = []

        for file_info in info:
            if self._isCheckedOutByOther(file_info):
                if fast_fail:
                    return file_info
                else:
                    checked_out.append(file_info)

        return checked_out

    def add(self, path=None, flags=None):
        """
        Adds the given path to the current client.

        Args:
            path (string): Path to add to client. Will use self.getCurrentScene() if None given.

            flags (list): Extra flags to pass to add command

        Returns:
            (Any): Result of file being added to client.
        """
        return self.runPath('add', path=path, flags=flags)

    def checkout(self, path=None, flags=None):
        """
        Checkouts the given path from the current client.

        Args:
            path (string): Path to check out from client. Will use self.getCurrentScene() if None given.

            flags (list): Extra flags to pass to check out ("edit") command

        Returns:
            (Any): Result of file being checked out from client.
        """
        return self.runPath('edit', path=path, flags=flags)

    def _runActions(self, command, actions, statement=None):
        files = actions[command]
        if files:

            for file_path in files:
                self.display(statement + file_path)

            return self.runPath(command, path=files)

        return None

    def makeAvailable(self, write_method=None, add=True, *args, **kwargs):
        """
        Used to write file(s) to disk while using Perforce to make sure file is writable.
        Pass the keyword "path", with a string path, or a list of paths. If not, current scene will be used.

        Args:
            write_method (method): Function that writes the file. Args and Kwargs will be passed ot this method.

            add (boolean): If True, will attempt to add file if not in client.

        Returns:
            (dictionary): Results of all the actions done for each file.
        """
        path = kwargs.get('path')
        info = self.getInfo(path=path)

        actions = OrderedDict()
        actions['sync'] = []
        actions['edit'] = []
        actions['add'] = []
        actions['failed'] = []
        results = deepcopy(actions)

        for file_info in info:
            file_path = file_info['clientFile']

            if 'notInClient' in file_info:
                if add:
                    # add file to p4 since it is not in p4
                    actions['add'].append(file_path)
            else:
                # if not latest, get latest.
                if not self._isLatest(file_info):
                    actions['sync'].append(file_path)

                # cant write to this file!
                if self._isCheckedOutByOther(file_info):
                    actions['failed'].append(file_path)
                    continue

                # file is already editable by user
                if self._isInChangelist(file_info):
                    continue

                # file needs to be checked out
                actions['edit'].append(file_path)

        # raise any files that are not writeable
        if actions['failed']:
            raise EnvironmentError('Cannot write the following files: ' + ', '.join(actions['failed']))

        # sync, edit, write files, then add
        results['sync'].append(self._runActions('sync', actions, 'File is not latest! Getting latest on: '))
        results['edit'].append(self._runActions('edit', actions, 'Checking out: '))

        if write_method:
            write_method(*args, **kwargs)

        results['add'].append(self._runActions('add', actions, 'Adding: '))
        return results


def getDepots():
    """
    Convenience method for getting all depots user has.

    Returns:
        (dictionary): Depot name as key, list as value with client path as first index, and client name as second.
    """
    p4 = Perforce()
    with p4.connect():
        depots = p4.getDepots()

    return depots


def makeAvailable(write_method=None, path=None, *args, **kwargs):
    """
    Convenience method for making a file available.

    Args:
        write_method (method): Function that writes the file. Args and Kwargs will be passed ot this method.

        path (string or iterable): Path to make available.

    Returns:
        (dictionary): Results of all the actions done for each file.
    """
    p4 = Perforce()
    with p4.connect():
        results = p4.makeAvailable(write_method=write_method, path=path, *args, **kwargs)

    return results
