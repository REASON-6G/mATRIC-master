 # Contributing to mATRIC

🎉 Welcome and thank you for your interest in contributing to **mATRIC** – the Multi-Access Technology Intelligent Controller developed by the [Smart Internet Lab, University of Bristol](https://www.bristol.ac.uk/smart) as part of the [REASON 6G Project](https://reason-open-networks.ac.uk/about/).

This project enables intelligent control and optimisation across heterogeneous wireless access networks, including 5G, Wi-Fi, and LiFi. We welcome contributions from researchers, developers, students, and collaborators across academia and industry.

---

## 🚀 Getting Started

### 1. Fork the repository

Click the **Fork** button in the top-right corner to create your own copy.

### 2. Clone your fork locally

```bash
git clone https://github.com/your-username/mATRIC-master.git
cd mATRIC-master
```

### 3. Create a branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Start the app with Docker

```bash
docker compose up --build
```

Make sure to configure your `.env` file. You can copy from `.env.example` and generate secure keys:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Update the following values:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

---

## ✅ Coding Standards

- **Backend**: Follow [PEP8](https://peps.python.org/pep-0008/), use type hints and Pydantic models.
- **Frontend**: Use ESLint rules, TypeScript best practices, and Chakra UI for components.
- **Tests**: Use [Pytest](https://docs.pytest.org/) or React Testing Library.
- **Docs**: Update or add `.md` files where appropriate.

---

## 📂 Commit Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org):

```
<type>(<scope>): <description>
```

**Examples**:
- `fix(api): correct AP metrics sync`
- `docs: update frontend deployment guide`
- `feat(controller): add support for LiFi integration`

Valid types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

---

## 📤 Submitting a Pull Request

1. Push your branch:

```bash
git push origin feature/your-feature-name
```

2. Open a Pull Request to the `master` branch on GitHub

Include in your PR:
- A clear summary of your changes
- Any linked issues (e.g., `Closes #12`)
- Screenshots for UI or visual changes
- Notes about any breaking changes

Your contribution will be reviewed by a maintainer and may be merged or returned with suggestions.

---

## 🐞 Reporting Issues

Please use the [GitHub Issues page](https://github.com/REASON-6G/mATRIC-master/issues) to report:

- 🐛 Bugs or errors
- ❓ Questions about usage
- 💡 Feature suggestions
- 📉 Performance issues

Include:
- Steps to reproduce
- Screenshots (if applicable)
- Error logs or outputs
- Expected vs actual behaviour

---

## 🧠 Academic & Research Contributions

If your contribution is based on research or academic work, please:

- Cite your paper or preprint (if applicable)
- Share anonymised datasets or benchmarking scripts
- Use `contrib/your-name/` for research modules or prototypes

Please also cite mATRIC if it supports your publication. Citation metadata is available in the [`CITATION.cff`](./CITATION.cff) file.

---

## 📜 License

By contributing, you agree that your code will be released under the [BSD 3-Clause License](./LICENSE), in line with the rest of the project.

---

## 📫 Contact

For general questions, collaborations, or institutional partnerships:

📧 [smart-internet-lab-contact@bristol.ac.uk](mailto:smart-internet-lab-contact@bristol.ac.uk)
