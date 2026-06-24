# voice-profile

A skill for capturing your authentic writing voice as a set of reusable rules and applying them as a context layer over any AI-assisted draft.

## The problem it solves

I can't really code, so I lean on AI for a lot of my work, including writing. And for a while, everything it produced in my name sounded like the same person. Confident, organized, slightly too smooth. I'd ask it to write a post or an email in my voice, and it would produce something that was roughly right in content but clearly not mine in feel. The sentences landed in ways I'd never land them, and the words it reached for weren't the words I reach for.

The problem wasn't that the models were bad at writing. They're good at writing. The problem was that "write in my voice" is not a spec. It tells the model to do something without giving it anything real to work from. So it does what it does by default, which is produce clean, competent prose that sounds like a reasonable approximation of a professional writer.

I built a voice profile to fix that. I pulled together things I'd actually written and looked for what showed up consistently across all of them: how long my sentences tend to run, the words I never use, how I open and close paragraphs, how I handle uncertainty. I wrote those patterns down as explicit rules, added a handful of raw sentences from my own writing as examples, and now I paste that document into context before any writing task where my voice matters. The output is noticeably different. It still needs a cleanup pass afterward, which is what the ai-proof skill in this series handles, but the starting point is much closer to something I'd actually write.

If you put your name on writing that AI helps with, this is worth doing once.

## How it works

1. Gather 5 to 10 pieces you wrote without AI help, across a few formats if possible.
2. Extract the consistent patterns: sentence length, vocabulary, conjunctions you use, things you avoid, tone, how you open and close.
3. Write those patterns down as explicit rules, and add 3 to 5 raw examples from your own writing as anchors.
4. Keep the profile in a reference file (300 to 600 words works well).
5. Paste the profile into context before every writing task in your voice, before the request, not after.
6. Run a cleanup pass on the draft to strip AI's default rhythms out. The ai-proof skill pairs naturally here.
7. Review the profile every few months and update it as your writing evolves.

See `SKILL.md` for the full method.

## Install

```
curl -fsSL https://github.com/jdurey/skills/tarball/main | tar -xz && mv jdurey-skills-*/voice-profile . && rm -rf jdurey-skills-*
```

## Why it's public

I built this inside an AI OS I put together to run my own work. The version here is scrubbed, standalone, and contains none of my private setup or personal voice rules. It's the method anyone can use to build their own profile. It's one of a series of skills I'm writing up.
