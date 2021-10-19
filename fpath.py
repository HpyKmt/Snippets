import os
import shutil
import re


__version__ = '0.0.0'


class Prompt:
    """ Prompt user for file/directory path from console user interface"""

    def __init__(self, msg='Drag and drop your file/folder: '):
        """
        Constructor
        :param msg: message to prompt user to input file or folder.
        """
        self.msg = msg

    def get_file(self):
        while True:
            path_in = input(self.msg).replace('"', '')
            if os.path.isfile(path_in):
                print(f'INFO: {path_in} is a valid file path.')
                return path_in
            else:
                print(f'ERROR: {path_in} is not a valid file path!')

    def get_dir(self):
        while True:
            path_in = input(self.msg).replace('"', '')
            if os.path.isdir(path_in):
                print(f'INFO: {path_in} is a valid directory path.')
                return path_in
            else:
                print(f'ERROR: {path_in} is not a valid directory path!')

    def get_file_or_dir(self):
        while True:
            path_in = input(self.msg).replace('"', '')
            if os.path.isdir(path_in):
                print(f'INFO: {path_in} is a valid directory path.')
                return path_in
            elif os.path.isfile(path_in):
                print(f'INFO: {path_in} is a valid file path.')
                return path_in
            else:
                print(f'ERROR: {path_in} is not a valid directory path!')


class Mapper:
    """ フォルダをマッピングする。
    効率化の為、returnせずにyieldする。
    変数はファイルを探すか、フォルダを探すか、再帰するか、しないか。"""

    def __init__(self, path_in):
        """
        Constructor
        :param path_in: either file path or folder path
        """
        self.path_in = path_in

    def path_generator(self, search_type='file', recursive=True):
        """
        Path Generator
        :param search_type: 'file' or 'dir' as string
        :param recursive: True or False as boolean
        :return: Yield absolute path as string if self.path_in is valid
        Raise ValueError if self.path_in is neither a file nor a folder.
        """
        # 渡されたパスがフォルダであることを確認する。
        if os.path.isdir(self.path_in):
            # ファイル
            if search_type == 'file':
                # 再帰
                if recursive:
                    for root, dirs, files in os.walk(self.path_in):
                        for file in files:
                            yield os.path.join(root, file)
                # 子階層のみ
                else:
                    for i in os.listdir(self.path_in):
                        p = os.path.join(self.path_in, i)
                        if os.path.isfile(p):
                            yield p
            # フォルダ
            elif search_type == 'dir':
                # 再帰
                if recursive:
                    for root, dirs, files in os.walk(self.path_in):
                        for sub_dir in dirs:
                            yield os.path.join(root, sub_dir)
                # 子階層のみ
                else:
                    for i in os.listdir(self.path_in):
                        p = os.path.join(self.path_in, i)
                        if os.path.isdir(p):
                            yield p
        # 渡されたパスがファイルの場合
        elif os.path.isfile(self.path_in):
            yield self.path_in
        # 渡されたパスがファイルでもフォルダでも無い場合
        else:
            raise ValueError(f'self.path_in "{self.path_in}" is not a valid path in this system!')


class Filter:
    """ 通常はファイルやフォルダの名称や拡張子で目的のファイルを取得する.
    複雑な場合は正規表現を使って選別する。"""
    @staticmethod
    def by_base_name(path_in, base_name='__pycache__', search_type='dir', recursive=True):
        """
        Search file or folder by base name
        :param path_in: Parent Folder
        :param base_name: file name or folder name (case insensitive)
        :param search_type: 'file' | 'dir'
        :param recursive: True | False
        :return: Absolute Path
        """
        for fp in Mapper(path_in).path_generator(search_type=search_type, recursive=recursive):
            if os.path.basename(fp).upper() == base_name.upper():
                yield fp

    @staticmethod
    def by_extension(path_in, extension='.txt', recursive=True):
        """
        Search files by extension
        :param path_in: parent folder
        :param extension:
            File extension with dot e.g. '.txt'.
            Empty string in case of no extension e.g. ''
        :param recursive: True | False
        :return: absolute file path
        """
        for fp in Mapper(path_in).path_generator(search_type='file', recursive=recursive):
            if os.path.splitext(fp)[1].upper() == extension.upper():
                yield fp

    @staticmethod
    def by_regex(path_in, regex='.*', search_type='file', recursive=True):
        """
        Search files or folders by regular expression
        :param path_in: parent folder
        :param regex: regular expression to find the matching path pattern
        :param search_type: 'file' | 'dir'
        :param recursive: True | False
        :return: absolute file or folder path
        """
        pattern = re.compile(regex, re.IGNORECASE)
        for fp in Mapper(path_in).path_generator(search_type=search_type, recursive=recursive):
            if pattern.match(fp):
                yield fp


class Sorter:
    def __init__(self, path_list):
        self.pth_lst = path_list

    def sort_by_date_modified(self):
        """
        Sort path by file modified date in ascending order
        :return: yield a path
        """
        for m_time, fp in sorted([(os.path.getmtime(fp), fp) for fp in self.pth_lst]):
            yield fp


class Dummy:
    @staticmethod
    def create_tree(dir_in, depth=2, count=5):
        """
        テスト用のダミーファイルとダミーフォルダを作成する。
        :param dir_in: ダミー作成用のルートディレクトリ
        :param depth: サブディレクトリ作成時の再帰コールの制限数
        :param count: 各階層で子要素の作成数
        :return: 無し
        """
        # 渡されたパスがフォルダの場合、フォルダを削除して空フォルダを再構築する。
        if os.path.isdir(dir_in):
            shutil.rmtree(dir_in)
            os.makedirs(dir_in)
        else:
            raise ValueError(f'Path {dir_in} does not exist.')

        # ループ
        for i in range(count):
            # 現在の位置確認
            print(f'depth={depth}, index={i}')
            # ファイルを作成
            for ext in ['.txt', '.csv', '.tsv', '_']:
                fp = os.path.join(dir_in, f'{depth}-{i}{ext}')
                with open(fp, 'w') as f:
                    f.write('x')

            # フォルダを作成
            if depth > 0:
                dp = os.path.join(dir_in, f'{depth}-{i}')
                os.makedirs(dp)
                # 再帰
                Dummy.create_tree(dp, depth=depth-1, count=count)

    @staticmethod
    def create_file_by_size(dir_in, file_name='dummy.dat', file_size=1024*1024):
        """
        指定したサイズのダミーファイルを作成する。
        :param dir_in: 親フォルダ
        :param file_name: ファイルの名称
        :param file_size: ファイルのサイズ
        1KB = 1024
        1MB = 1024 * 1024
        1GB = 1024 * 1024 * 1024
        :return: 無し
        """
        fp = os.path.join(dir_in, file_name)
        with open(fp, 'wb') as f:
            f.seek(file_size)
            f.write(b'/0')
        print(f'File {fp} has been created.')
        print(f'File size is {os.path.getsize(fp)}.')


def _test():
    Prompt(msg='D&D Your File: ').get_file()


if __name__ == '__main__':
    _test()
