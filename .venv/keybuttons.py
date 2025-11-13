import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--package', required=True)
parser.add_argument('--repo', required=True)
parser.add_argument('--test-mode', choices=['local', 'remote'], required=True)
parser.add_argument('--version', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

config = {
    'package': args.package,
    'repo': args.repo,
    'test_mode': args.test_mode,
    'version': args.version,
    'output': args.output
}

for key, value in config.items():
    print(f"{key}: {value}")