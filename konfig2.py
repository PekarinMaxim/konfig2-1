import argparse
import sys
import os
import urllib.request
import json
import re


def get_package_metadata(package_name, version, repo_url):
    """Получает метаданные пакета из репозитория"""
    try:
        # Формируем URL
        if repo_url.startswith(('http://', 'https://')):
            if 'pypi.org' in repo_url or 'pypi.org' in repo_url:
                url = f"https://pypi.org/pypi/{package_name}/{version}/json"
            else:
                url = f"{repo_url}/{package_name}/{version}/json"
        else:
            local_path = os.path.join(repo_url, package_name, version, f"{package_name}-{version}.dist-info",
                                      "metadata.json")
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise ValueError(f"Метаданные пакета не найдены по пути: {local_path}")
        # Загружаем данные для удаленного репозитория
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return json.loads(response.read().decode('utf-8'))
            else:
                raise ValueError(f"Не удалось получить данные о пакете. HTTP статус: {response.status}")
    except Exception as e:
        raise ValueError(f"Ошибка при получении метаданных пакета: {e}")
def extract_dependencies(metadata):
    """Извлекает зависимости из метаданных пакета"""
    dependencies = []
    try:
        # Получаем информацию о зависимостях из полей метаданных
        info = metadata.get('info', {})
        requires_dist = info.get('requires_dist', [])
        requires = info.get('requires', [])
        run_requires = info.get('run_requires', [])
        if requires_dist:
            for dep in requires_dist:
                dep_name = re.split(r'[<>=!~]', dep.strip())[0].strip()
                if dep_name and dep_name not in dependencies:
                    dependencies.append(dep_name)
        if not dependencies and requires:
            for dep in requires:
                dep_name = re.split(r'[<>=!~]', dep.strip())[0].strip()
                if dep_name and dep_name not in dependencies:
                    dependencies.append(dep_name)
        if not dependencies and run_requires:
            for req in run_requires:
                if isinstance(req, dict) and 'requires' in req:
                    for dep in req['requires']:
                        dep_name = re.split(r'[<>=!~]', dep.strip())[0].strip()
                        if dep_name and dep_name not in dependencies:
                            dependencies.append(dep_name)
        return dependencies
    except Exception as e:
        raise ValueError(f"Ошибка при извлечении зависимостей: {e}")


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
        # Вывод настроенных параметров
        print("Настроенные параметры:")
        for key, value in config.items():
            print(f"{key}: {value}")
        print("\nПолучение информации о зависимостях...")
        # Получаем метаданные пакета
        metadata = get_package_metadata(args.package, args.version, args.repo)
        print(metadata)
        # Извлекаем зависимости
        dependencies = extract_dependencies(metadata)
        # Выводим все прямые зависимости (требование этапа 4)
        print(f"\nПрямые зависимости пакета {args.package} версии {args.version}:")
        if dependencies:
            for i, dep in enumerate(dependencies, 1):
                print(f"{i}. {dep}")
        else:
            print("Зависимости не найдены")
        dependencies_data = {
            'package': args.package,
            'version': args.version,
            'dependencies': dependencies
        }
        # Сохраняем в файл для использования в следующем этапе
        with open('dependencies_cache.json', 'w', encoding='utf-8') as f:
            json.dump(dependencies_data, f, ensure_ascii=False, indent=2)
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
#python script.py --package requests --version 2.28.0 --repo https://pypi.org --test-mode remote --output graph.json
#python script.py --package numpy --version 1.24.0 --repo https://pypi.org --test-mode remote --output deps.json
#python script.py --package mypackage --version 1.0.0 --repo /path/to/local/packages --test-mode local --output local_deps.json
