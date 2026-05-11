# 部署到 GitHub Pages — 操作步骤

你的网站文件已在 `D:\LDCB` 中准备就绪，只需在电脑上执行以下步骤即可上线。

## 第 1 步：创建 GitHub 仓库

1. 浏览器打开 https://github.com/new
2. **Repository name 必须填**：`SANS41478.github.io`
3. 选择 **Public**（公开仓库）
4. **不要**勾选任何初始化选项（README 等）
5. 点击 "Create repository"
6. 仓库地址：`https://github.com/SANS41478/SANS41478.github.io.git`

## 第 2 步：初始化 Git 并推送

打开 **命令提示符（CMD）** 或 **PowerShell**，逐行执行：

```bash
# 进入项目目录
cd D:\LDCB

# 如果之前有残留的 .git 目录，先删除
rmdir /s /q .git

# 初始化 Git 仓库
git init
git branch -m main

# 配置身份
git config user.name "LD"
git config user.email "1589522508@qq.com"

# 暂存所有文件
git add -A

# 提交
git commit -m "Initial commit: personal website with PingFang SC font"

# 添加远程仓库
git remote add origin https://github.com/SANS41478/SANS41478.github.io.git

# 推送到 GitHub（会提示输入密码）
git push -u origin main
```

推送时：用户名填 `SANS41478`，密码填你的 Personal Access Token。

## 第 3 步：启用 GitHub Pages

1. 打开 https://github.com/SANS41478/SANS41478.github.io/settings/pages
2. Source 选择 **"Deploy from a branch"**
3. Branch 选择 `main`，目录选 `/ (root)`
4. 点击 **Save**
5. 等待 1-2 分钟，你的网站就上线在：**https://SANS41478.github.io/**

> 使用 `SANS41478.github.io` 作为仓库名的好处：网站地址直接是 `https://SANS41478.github.io/`，不需要 `/子目录` 后缀。

## 以后更新网站

修改文件后，在 `D:\LDCB` 中执行：

```bash
git add -A
git commit -m "描述你改了什么"
git push
```

GitHub Pages 会自动重新部署，通常 1 分钟内生效。
