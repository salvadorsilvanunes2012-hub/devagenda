import os

FICHEIRO_AGENDA = "minha_agenda.txt"

def carregar_tarefas():
    if not os.path.exists(FICHEIRO_AGENDA):
        return []
    with open(FICHEIRO_AGENDA, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f.readlines()]

def guardar_tarefa(tarefa):
    with open(FICHEIRO_AGENDA, "a", encoding="utf-8") as f:
        f.write(tarefa + "\n")

def main():
    while True:
        print("\n--- 🕶️ A MINHA AGENDA SECRETA ---")
        print("1. Ver tarefas")
        print("2. Adicionar tarefa")
        print("3. Sair")
        
        opcao = input("\nEscolhe uma opção: ")
        
        if opcao == "1":
            tarefas = carregar_tarefas()
            if not tarefas:
                print("\n[A tua agenda está vazia!]")
            else:
                print("\nAs tuas tarefas:")
                for i, t in enumerate(tarefas, 1):
                    print(f"{i}. {t}")
                    
        elif opcao == "2":
            nova = input("Qual é a tarefa/compromisso? ")
            if nova.strip():
                guardar_tarefa(nova)
                print("✅ Tarefa guardada com sucesso!")
                
        elif opcao == "3":
            print("Até logo!")
            break
        else:
            print("Opção inválida, tenta outra vez.")

if __name__ == "__main__":
    main()