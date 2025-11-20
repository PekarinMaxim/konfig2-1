import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser(description='Анализатор зависимостей пакетов')

    # Аргументы для парсера
    parser.add_argument('--package', required=True, help='Имя анализируемого пакета')
    parser.add_argument('--repo', required=True, help='URL или путь к репозиторию')
    parser.add_argument('--test-mode', choices=['local', 'remote'], required=True, help='Режим работы')
    parser.add_argument('--version', required=True, help='Версия пакета')
    parser.add_argument('--output', required=True, help='Имя файла для графа')

    args = parser.parse_args()

    # Обработка ошибок
    try:
        if args.test_mode == 'local':
            if not os.path.exists(args.repo):
                raise ValueError(f"Локальный путь не существует: {args.repo}")
        else:
            if not args.repo.startswith(('http://', 'https://')):
                raise ValueError(f"Неправильная ссылка: {args.repo}")

        config = {
            'package': args.package.strip(),
            'repo': args.repo,
            'test_mode': args.test_mode,
            'version': args.version.strip(),
            'output': args.output
        }

        # Вывод
        print("Настроенные параметры:")
        for key, value in config.items():
            print(f"{key}: {value}")

    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
#python script.py --package requests --repo https://pypi.org --test-mode remote --version 2.28.0 --output deps.json