import prompt

def welcome():
    print('\nПервая попытка запустить проект!')
    print('\n***')
    while True:
        print('<command> exit - выйти из программы')
        print('<command> help - справочная информация')
        print('Введите команду: ', end='')
        command = prompt.string('')
        if command == 'exit':
            break
        elif command == 'help':
            continue
        else:
            print(f'Неверная команда: {command}')
