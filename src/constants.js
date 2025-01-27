// constants.js

export const ensureUniqueKeys = (stories) => {
    const seen = new Set();
    return stories.map((story) => {
      let key = story.key;
      while (seen.has(key)) {
        key = `${key}_${Math.random().toString(36).substr(2, 9)}`;
      }
      seen.add(key);
      return { ...story, key };
    });
  };
  
  export const userStories = ensureUniqueKeys([
    {
      key: 77,
      user_story:
        "As an organizer, I want predictive analysis for attendee numbers based on past data.",
      epic: "AI-powered Analytics",
    },
    {
      key: 73,
      user_story:
        "As a researcher, I want my paper content analyzed for key insights using NLP.",
      epic: "Reporting",
    },
    {
      key: 99,
      user_story:
        "As a user, I want to access the system from my mobile device so that I have flexibility.",
      epic: "User Authentication",
    },
    {
      key: 47,
      user_story:
        "As a researcher, I want to submit a paper so that I can share my work.",
      epic: "Payment Integration",
    },
    {
      key: 91,
      user_story:
        "As an admin, I want AI-powered analytics to track conference metrics.",
      epic: "Automated Review Assignment",
    }
    // {
    //   key: 41,
    //   user_story:
    //     "As a researcher, I want to submit a paper so that I can share my work.",
    //   epic: "Chatbot Integration",
    // },
    // {
    //   key: 51,
    //   user_story:
    //     "As a user, I want to create an account so that I can access the system.",
    //   epic: "User Profile Management",
    // },
    // {
    //   key: 48,
    //   user_story:
    //     "As a reviewer, I want to review submissions so that I can provide feedback.",
    //   epic: "AI-driven Recommendations",
    // },
    // {
    //   key: 88,
    //   user_story:
    //     "As an organizer, I want predictive analysis for attendee numbers based on past data.",
    //   epic: "Event Scheduling",
    // },
    // {
    //   key: 28,
    //   user_story:
    //     "As an organizer, I want to schedule events so that attendees know the timetable.",
    //   epic: "Automated Review Assignment",
    // },
    // {
    //   key: 64,
    //   user_story:
    //     "As a user, I want to interact with a chatbot for quick assistance.",
    //   epic: "Reporting",
    // },
    // {
    //   key: 3,
    //   user_story:
    //     "As a researcher, I want my paper content analyzed for key insights using NLP.",
    //   epic: "AI-driven Recommendations",
    // },
    // {
    //   key: 47,
    //   user_story:
    //     "As a user, I want to interact with a chatbot for quick assistance.",
    //   epic: "Natural Language Processing",
    // },
    // {
    //   key: 36,
    //   user_story:
    //     "As an organizer, I want to create a conference so that I can manage events.",
    //   epic: "Automated Review Assignment",
    // },
    // {
    //   key: 29,
    //   user_story:
    //     "As an admin, I want AI-powered analytics to track conference metrics.",
    //   epic: "Chatbot Integration",
    // },
  ]);
  