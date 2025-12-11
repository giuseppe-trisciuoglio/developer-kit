# Frontend Skills Guide

Questa guida raccoglie e documenta le skill frontend disponibili nel Developer Kit Claude Code, con focus su best practice, architetture, testing, automazione e integrazione AI per applicazioni web moderne.

---

## Indice

1. Introduzione alle skill frontend
2. Architetture e pattern supportati
3. Skill disponibili
4. Esempi pratici
5. Best practice
6. Come contribuire

---

## 1. Introduzione alle skill frontend

Le skill frontend sono moduli riutilizzabili che aiutano Claude Code a:
- Generare, analizzare e refactorizzare codice frontend (React, Vue, Angular, Svelte, ecc.)
- Automatizzare test end-to-end e unitari (Jest, Cypress, Playwright)
- Ottimizzare performance, accessibilità e sicurezza
- Integrare AI e automazioni (es. generazione componenti, prompt engineering)

## 2. Architetture e pattern supportati

- **Component-based**: React, Vue, Angular, Svelte
- **State management**: Redux, Zustand, Vuex, Context API
- **Testing**: Jest, Testing Library, Cypress, Playwright
- **Styling**: CSS-in-JS, Tailwind, SCSS, CSS Modules
- **API Integration**: REST, GraphQL, WebSocket
- **AI Integration**: Prompt engineering, generazione automatica UI

## 3. Skill disponibili

| Skill                                      | Scopo                                 | Tecnologie chiave           |
|--------------------------------------------|---------------------------------------|-----------------------------|
| frontend-react-component-patterns          | Generazione e refactoring componenti  | React, TypeScript           |
| frontend-vue-component-patterns            | Best practice componenti Vue          | Vue, Composition API        |
| frontend-angular-service-patterns          | Servizi e dependency injection        | Angular, RxJS               |
| frontend-testing-jest-patterns             | Test unitari e di integrazione        | Jest, Testing Library        |
| frontend-testing-cypress-patterns          | Test end-to-end                      | Cypress, Playwright          |
| frontend-accessibility-patterns            | Ottimizzazione accessibilità          | ARIA, Lighthouse            |
| frontend-performance-optimization          | Ottimizzazione bundle e rendering     | Webpack, Vite, React Profiler|
| frontend-ai-prompt-engineering             | Prompt engineering per UI             | Claude, OpenAI, LangChain    |

## 4. Esempi pratici

- Generazione automatica di componenti React con prop validation
- Refactoring di componenti Vue per performance
- Test end-to-end Cypress per flussi utente critici
- Ottimizzazione accessibilità con audit automatici
- Prompt engineering per generazione UI dinamica

## 5. Best practice

- Separazione tra logica e presentazione
- Test unitari e end-to-end per ogni feature
- Validazione prop e tipi
- Ottimizzazione bundle e lazy loading
- Accessibilità by design
- Sicurezza: XSS, CSRF, CORS

## 6. Come contribuire

1. Crea una nuova skill in `skills/frontend/<skill-name>/SKILL.md`
2. Segui il template ufficiale (frontmatter, istruzioni, esempi)
3. Documenta dipendenze e comandi
4. Aggiorna questa guida con la nuova skill
5. Invia una PR con descrizione e esempi

---

**Questa guida è in continua evoluzione: contribuisci per arricchire le skill frontend!**
