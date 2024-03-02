import numpy as np
import tkinter as tk
from tkinter import messagebox
import os
import colorsys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tempfile
import atexit


def create_lab_color_chart(L_valores, a_valores, b_valores, imagem_path):
    try:
        # Carrega a imagem
        imagem = plt.imread(imagem_path)

        # Cria uma figura e um eixo
        fig, ax = plt.subplots()

        # Exibe a imagem como fundo do gráfico
        ax.imshow(imagem, extent=[-100, 100, -100, 100], alpha=1)

        # Gráfico de dispersão para pontos de cor LAB
        scatter = ax.scatter(
            a_valores, b_valores,
            color=['none' if L >= 0 and a >= 0 else 'none' for L, a in zip(L_valores, a_valores)],
            edgecolors='black', linewidths=1.5
        )

        # Anota pontos no gráfico
        for i, txt in enumerate(zip(a_valores, b_valores)):
            ax.annotate(f'({txt[0]};{txt[1]})', (a_valores[i], b_valores[i]), textcoords="offset points",
                        xytext=(0, 5), ha='center', va='bottom')

        # Adiciona rótulos e título
        ax.set_ylabel('a*')
        ax.set_xlabel('b*')
        ax.set_title('CIELab')

        # Adiciona linhas de referência para os eixos X e Y
        ax.axhline(0, color='black', linewidth=0.7, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.5, linestyle='--')

        # Configurações de grade
        plt.grid(True, linestyle='--', alpha=0.6)

        # Define limites dos eixos
        ax.set_xlim(-100, 100)
        ax.set_ylim(-100, 100)

        # Adiciona uma barra de gradiente preto e branco
        cax = fig.add_axes([0.85, 0.1, 0.04, 0.79])
        cmap = plt.cm.gray
        norm = plt.Normalize(0, 100)
        cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cax)
        cb.set_label('L*')

        # Adiciona um ponto na barra de cores
        for L in L_valores:
            normalized_point = L
            cb.ax.plot([0, 1], [normalized_point, normalized_point],
                       color='red', linewidth=5, marker='_', markersize=8, label='Manual Point')

        # Adiciona a figura à lista de figuras
        figures.append(fig)

        # Exibe o gráfico
        plt.show()

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exibir o gráfico: {str(e)}")


def generate_color_wheel():
    num_points = 360
    hues = np.linspace(0, 1, num_points)
    saturations = np.linspace(0, 1, num_points)
    lightness = 0.5  # Luminosidade em 50%

    # Cria uma grade 2D de valores
    hsl_values = np.array([[hue, saturation, lightness]
                          for hue in hues for saturation in saturations])

    # Converte para RGB
    rgb_values = np.array([colorsys.hls_to_rgb(h, l, s)
                          for h, s, l in hsl_values])

    # Reformula os arrays para plotagem
    hues = hsl_values[:, 0].reshape((num_points, num_points))
    saturations = hsl_values[:, 1].reshape((num_points, num_points))
    rgb_values = rgb_values.reshape((num_points, num_points, 3))

    # Plota a roda de cores ajustada ao espaço de cores LAB
    fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_direction(1)
    ax.set_theta_offset(np.pi / 6.0)
    ax.set_position([0, 0, 1, 1])  # Ajusta a posição e o tamanho
    ax.set_rlabel_position(1)

    # Adiciona escala de 0 a 100 ao longo do raio
    r_ticks = np.linspace(0, 1, 6)
    r_labels = [f'{int(t*100)}' for t in r_ticks]
    ax.set_yticks(r_ticks)
    ax.set_yticklabels(r_labels, color='gray', fontsize=8)

    c = ax.pcolormesh(hues * 2 * np.pi, saturations, rgb_values)

    # Remove rótulos e linhas de grade dos eixos
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(False)

    # Função para excluir o arquivo temporário no encerramento do programa
    def excluir_arquivo_temporario(file_path):
        os.unlink(file_path)

    # Criar um arquivo temporário
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        image_path = temp_file.name

    # Salva o gráfico gerado como um arquivo de imagem
    image_path = 'color_wheel.png'
    plt.savefig(image_path, dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()

    # Registrar a função para excluir o arquivo temporário no encerramento do programa
    atexit.register(excluir_arquivo_temporario, image_path)

    return image_path

def main():
    # Cria a janela principal
    root = tk.Tk()
    root.title("LAB Color Chart")

    # Define o ícone da janela
    root.iconbitmap("C:/Users/arlie/OneDrive/CIELAB/TESTE/CIELAB.ico")

    # Rótulo para instrução
    version_label = tk.Label(
        root, text='Insira os valores de L*a*b*:', font=('Arial Bold', 9))
    version_label.pack(expand=True)

    # Define as dimensões da janela
    window_width = 400
    window_height = 200

    # Obtém as dimensões da tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcula a posição central da janela
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    # Define a geometria da janela
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    
    def adicionar():
        try:
            L_valores = float(L_entry.get())
            a_valores = float(a_entry.get())
            b_valores = float(b_entry.get())

            points.append((L_valores, a_valores, b_valores))

            # Gera a roda de cores
            imagem_path = generate_color_wheel()

            # Criar uma lista de todos os pontos, incluindo os pontos existentes e o novo ponto
            all_L_values = [point[0] for point in points]
            all_a_values = [point[1] for point in points]
            all_b_values = [point[2] for point in points]

            # Exibe o gráfico de cores LAB usando a roda de cores gerada
            create_lab_color_chart(all_L_values, all_a_values, all_b_values, imagem_path)

        except ValueError:
            messagebox.showerror(
                "Erro", "Por favor, insira valores válidos para L*a*b*.")

    def limpar_entradas():
        L_entry.delete(0, 'end')
        a_entry.delete(0, 'end')
        b_entry.delete(0, 'end')
        points.clear()  # Limpa a lista de pontos

    # Lista para armazenar os pontos
    points = []

    # Cria o frame para os valores de LAB
    lab_frame = tk.Frame(root)
    lab_frame.pack(pady=10)

    # Cria os campos de entrada para os valores de LAB
    tk.Label(lab_frame, text="L*").grid(row=0, column=0)
    L_entry = tk.Entry(lab_frame)
    L_entry.grid(row=0, column=1)

    tk.Label(lab_frame, text="a*").grid(row=1, column=0)
    a_entry = tk.Entry(lab_frame)
    a_entry.grid(row=1, column=1)

    tk.Label(lab_frame, text="b*").grid(row=2, column=0)
    b_entry = tk.Entry(lab_frame)
    b_entry.grid(row=2, column=1)

    # Frame para conter os botões
    button_frame = tk.Frame(root)
    button_frame.pack()


    # Botão para adicionar ponto e abrir novo gráfico
    adicionar_novo_button = tk.Button(
        button_frame, text="Mostrar/Inserir", command=adicionar)
    adicionar_novo_button.pack(side=tk.LEFT, padx=5)

    # Botão para limpar as entradas
    limpar_entradas_button = tk.Button(
        button_frame, text="Limpar", command=limpar_entradas)
    limpar_entradas_button.pack(side=tk.LEFT, padx=5)


    # Botão para sair
    def fechar_programa():
        root.quit()
        root.destroy()
        for fig in figures:
            plt.close(fig)  # Fecha todas as figuras de plotagem

    exit_button = tk.Button(button_frame, text="Sair", command=fechar_programa)
    exit_button.pack(side=tk.LEFT, padx=5)

    version_label = tk.Label(
        root, text='2024 © LAB Color Chart v.1.1', font=('Arial Bold', 8))
    version_label.pack(expand=True)

    root.mainloop()


if __name__ == "__main__":
    # Lista para armazenar as figuras de plotagem
    figures = []
    main()
