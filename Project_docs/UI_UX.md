# UI/UX Design Document

**File name:** UI_UX.md  
**Version:** v1.0  
**Date:** 24 March 2026  

## 1.0 Purpose & Scope
This document outlines the comprehensive UI/UX design specifications for Antigravity, focusing on "Alex", the core AI voice assistant. It serves as the definitive guide for developers and designers to ensure a cohesive, accessible, and premium user experience across all platforms. The scope covers visual language, component libraries, screen layouts, and interaction patterns required to support a next-generation "AI Operating System" experience.

## 2.0 Design Philosophy
### Core design principles
1. **Frictionless Interaction:** Voice and text modalities should blend seamlessly.
2. **Ambient Intelligence:** The UI should recede, presenting information only when necessary (Smart Suggestions, Wake-Up Briefings).
3. **Clarity over Clutter:** Minimalist aesthetics to prevent cognitive overload during complex autonomous task execution.
4. **Instructive Feedback:** Clear indicators of system state (listening, processing, speaking, acting).

### Visual language
A futuristic yet welcoming aesthetic (Glassmorphism + Neo-Brutalism influences for structural clarity). Dark mode-first design to map to a "next-generation" AI feel, with organic, fluid states representing AI thinking.

### Design system overview
A modular, token-based design system tailored for responsive cross-platform scalability.

## 3.0 User Interface Components

### 3.1 Color System
We utilize a highly tailored, sleek dark-mode palette accentuating trust and technological advancement.

| Role | Color Name | Hex Code | Usage Rules |
|------|-----------|----------|-------------|
| Primary Background | Deep Void | `#0A0A0F` | Main app background (Dark Mode) |
| Surface | Ethereal Glass | `#16161D` | Cards, modals, elevated surfaces |
| Primary Accent | Electric Cyan | `#00F0FF` | Primary actions, active AI focus states |
| Secondary Accent | Neon Purple | `#9D4EDD` | Secondary actions, voice waveforms |
| Text Primary | Off White | `#F8F9FA` | Headings, primary body copy |
| Text Secondary | Slate Grey | `#A1A1AA` | Subtitles, placeholders, captions |
| Error | Crimson Alert | `#FF3366` | Destructive actions, system errors |
| Success | Spring Green | `#00E676` | Task completion, positive confirmations |

*Dark/light mode specifications:* Light mode replaces Deep Void with `#FAFAFA` and Surface with `#FFFFFF`, while adjusting text to `#121212` for primary. Accent colors remain vibrant but slightly darkened for contrast.

### 3.2 Typography
| Role | Font Family | Fallback |
|------|------------|----------|
| Headings | **Outfit** | sans-serif |
| Body | **Inter** | sans-serif |
| Data / Code | **JetBrains Mono** | monospace |

*Size Scale & Weight Rules:*
- H1: 48px, Semi-Bold (Hero, Wake-up briefing headers)
- H2: 32px, Medium (Screen titles)
- H3: 24px, Medium (Section headers, Card titles)
- Body Large: 18px, Regular (AI chat bubbles)
- Body Base: 16px, Regular (Standard UI text)
- Caption: 14px, Light (Timestamps, secondary data)

### 3.3 Spacing & Grid System
*Grid Layout:* 12-column liquid grid.

| Token | Value | rem (base 16px) | Usage |
|-------|-------|-----------------|-------|
| sp-xs | 4px | 0.25rem | Internal component padding |
| sp-sm | 8px | 0.5rem | Between tight elements (icons/text) |
| sp-md | 16px | 1.0rem | Standard padding, list items |
| sp-lg | 24px | 1.5rem | Section gaps, card padding |
| sp-xl | 32px | 2.0rem | Major structural spacing |
| sp-xxl| 48px | 3.0rem | Screen margins |

*Breakpoints:* Mobile (<768px), Tablet (768px - 1024px), Desktop (>1024px).

### 3.4 Component Library
- **Buttons:** Pill-shaped, 48px height for touch targets. Primary buttons have a soft `Electric Cyan` glow (`box-shadow: 0 0 15px rgba(0, 240, 255, 0.3)`).
- **Forms & inputs:** Underline or fully contained glass inputs. Focus states trigger border color change to Primary Accent.
- **Cards:** 16px border-radius, `Ethereal Glass` background, subtle 1px inner border (`rgba(255, 255, 255, 0.05)`).
- **Navigation:** Floating bottom pill on mobile; slim left-side rail on desktop.
- **Modals & overlays:** Full screen or centered glass panels with a heavy background blur (`backdrop-filter: blur(12px)`).
- **Loading states:** Fluid gradient skeleton screens or animated AI orb (breathing effect).
- **Error states:** Actionable error cards (Crimson Alert borders) providing direct paths to resolution (e.g., "Retry Search").

## 4.0 Screen Designs

### 4.1 Onboarding screens
Introduce Alex via voice and minimal text. Collect voice sample to establish behavior learning baseline.
```text
+-----------------------------------+
|              [logo]               |
|                                   |
|       "Hi, I'm Alex."             |
|                                   |
|   Hold the button and say         |
|   'Hello' to configure voice.     |
|                                   |
|            ( O )                  |
|          Hold to Talk             |
+-----------------------------------+
```

### 4.2 Dashboard/Home screen
The Wake-Up Briefing interface providing calendar, tasks, and system status directly.
```text
+-----------------------------------+
|  Good Morning, User.              |
|  Today: 3 Meetings, 2 Tasks       |
|                                   |
|  [ Card: Briefing Summary ]       |
|  "Your 10 AM is moved to 11 AM."  |
|                                   |
|  [ Card: Recent Files ]           |
|  - Q3_Report.pdf                  |
|                                   |
|      [====== Voice Wave ======]   |
|         [ Mic ]  [ Chat ]         |
+-----------------------------------+
```

### 4.3 Core feature screens
Chat/Execution Interface mixing voice transcription, text, and rich actionable widgets (booking cards, file previews, smart suggestions). Multi-turn conversation capability visually highlighted.

### 4.4 Settings screen
Access controls, API credentials (Google Calendar, WhatsApp, Integrations), memory/preference management.

### 4.5 Error & empty states
Playful but clear "System Offline", "I didn't catch that", or "No Files Found" with suggested next steps. 

## 5.0 User Experience Rules

### 5.1 Interaction patterns
- Voice input is the primary driver; text acts as fallback.
- Contextual intent switching (from scheduling a meeting to drafting an email seamlessly) without losing state.

### 5.2 Animation & transitions
- **Micro-animations:** Icons morphing (e.g., mic to stop button, sending to completed).
- **Transitions:** Screens slide in from right; modals fade and scale up (0.95 to 1.0) with an easing curve (`cubic-bezier(0.16, 1, 0.3, 1)`).

### 5.3 Feedback mechanisms
- Haptic feedback on mobile for button presses and task completion.
- Visual waveform modulation that reacts in real-time to user voice amplitude and AI response state.

### 5.4 Accessibility standards (WCAG 2.1)
- Contrast ratios of at least 4.5:1 for all text.
- Screen reader support via semantic HTML tags (`<nav>`, `<main>`, `<article>`).
- Touch targets strictly minimum `48x48px`.

## 6.0 Responsive Design
- **Mobile first approach:** Design optimizes for one-handed thumb reachability focusing the mic/chat input at the bottom of the screen.
- **Tablet layout:** Dual-pane layout (Navigation + Main content).
- **Desktop layout:** Multi-column dashboard (Rail + Chat View + Widget View).
- **Breakpoint behavior:** Fluid typography scaling via CSS `clamp()`.

## 7.0 User Experience Flows
- **Wake-up Flow:** User Opens App -> Briefing Summarized Voice Readout -> Prompts for actions -> Executes or ends.
- **Task Execution Flow:** User voices command -> Processing UI (Intent Parsing) -> Confirmation Modal (if unsafe action) -> Action Execution -> Success Toast/Voice.
- **Navigation patterns:** Flat hierarchy. Everything is accessible from chat; secondary UI (Settings/History) via sliding drawers.
- **Back navigation rules:** Swipe from left edge (mobile) or persistent breadcrumbs/back arrows targeting the prior conversational state.

## 8.0 Design Tokens
*Example export format for developer handoff:*
```css
:root {
  --color-bg-primary: #0A0A0F;
  --color-accent-primary: #00F0FF;
  --font-hero: 700 48px 'Outfit', sans-serif;
  --spacing-container: 32px;
  --radius-card: 16px;
  --shadow-glow: 0 0 15px rgba(0, 240, 255, 0.3);
}
```

## 9.0 Open Questions
1. Do we allow custom wake words for Alex, or just a universal button press/hotword?
2. Should the voice UI interrupt processing if the user starts speaking again?
3. How deep should the offline functionality extend regarding UI (cached vs disabled states)?

## 10.0 Next Steps
- Finalize high-fidelity Figma mockups based on ASCII wireframes.
- Prototype the Voice Waveform animation in code (WebGL/Canvas or CSS).
- Extract all design tokens into a JSON format for a CI/CD build process into frontend CSS variables.

## 11.0 Professional Sign-off
Prepared by: Senior UI/UX Design Team  
To be reviewed by: Lead Architecture and Development Teams  
*Designed for an AI Operating System to be frictionless, professional, and visually stunning.*
