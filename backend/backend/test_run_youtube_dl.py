from backend.run_youtube_dl import run_command_get_output
import os


def test_command_exec_stdout():
    command = 'ls'
    args = ['/']
    output = run_command_get_output(command, args, do_print=True, out_fn='/tmp/test_file.txt')
    assert 'var' in output

def test_command_exec_stderr():
    command = 'ls'
    args = ['/__does_not_exist__test']
    output = run_command_get_output(command, args, do_print=True, out_fn='/tmp/test_file.txt')
    assert 'No such file' in output

