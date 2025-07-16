# Page snapshot

```yaml
- banner:
  - text: Election
  - button "View Identity Cards": View Identity Cards 🎭
  - button "Game Information": Game Information ⓘ
  - button "Game Menu": Game Menu ☰
- status: "Action Phase Round 2 - Choose your actions 3 rounds until Legislation Phase C Charlie PC: 31 | Office: None ⚡ 2 AP"
- heading "Action Phase" [level=3]
- paragraph: You have 2 action points remaining.
- button "🎭 View Identity"
- log: Bob passes their turn. Charlie's turn.
- toolbar "Game Actions":
  - button "Pass turn to next player": Pass Turn
  - 'button "Fundraise - Cost: 1 Action Points"': Fundraise fundraise
  - 'button "Network - Cost: 1 Action Points"': Network network
  - 'button "Use Favor - Cost: 1 Action Points"': Use Favor use_favor
  - 'button "Support Legislation - Cost: 1 Action Points"': Support Legislation support_legislation
  - 'button "Oppose Legislation - Cost: 1 Action Points"': Oppose Legislation oppose_legislation
  - 'button "Sponsor Legislation - Cost: 2 Action Points"': Sponsor Legislation sponsor_legislation
  - 'button "Campaign - Cost: 2 Action Points"': Campaign campaign
- heading "🤫 Secret Opposition Commitment" [level=3]
- button "Close": ×
- paragraph:
  - strong: "⚠️ Secret Commitment:"
  - text: Your opposition will be hidden from other players until the legislation reveal.
- text: "Choose Legislation:"
- combobox "Choose Legislation:":
  - option "Select legislation..." [selected]
  - option "Protect The Children! (sponsored by Alice)"
- text: "PC to Commit (Secret):"
- spinbutton "PC to Commit (Secret):"
- button "🤫 Secretly Oppose"
- button "Cancel"
```