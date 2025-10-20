# tikz-spyzoombox

本工程使用 LaTeX + TikZ 实现了图像放大镜效果（spy box），能够在一张图中定义采样区域，并在指定位置绘制放大后的细节区域，同时支持自动连接线和参数化设置。

## 功能特点
- 使用 `tikz` 的 `spy` 库实现局部放大显示。
- 可通过参数设置采样框大小、放大倍数、线框宽度等。
- 自动计算放大框尺寸，无需手动调整。
- 可选择是否绘制连接线，支持自定义样式。

## 使用方法
1. 在 `figure` 目录下创建 `tikz` 子目录，将你的示例图片放在该目录下，并在 `spy_zoom_box.tex` 中修改 **图片路径**（`\figurepath`）及相关 **参数设置**。 
   编译命令如下：
   
   ```bash
   xelatex spy_zoom_box.tex
   ```
   
2. 在你的主文档 main.tex 中导入生成的 spy_zoom_box.pdf 文件，例如：

    ```
    \begin{figure}[htbp]
        \centering
        \includegraphics[width=0.8\textwidth]{figure/tikz/spy_zoom_box.pdf}
        \caption{局部放大示意图}
        \label{fig:zoom}
    \end{figure}
    ```