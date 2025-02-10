const personasWithTasks = [
  {
    id: 1,
    name: "Product Owner",
    role: "PO",
    tasks: [
      {
        taskId: 101,
        taskName: "user_story_generation",
        taskLabel: "User Story Generation",
        prompt: "As a Product Owner, your task is to generate high-quality user stories based on the provided project requirements and vision. Ensure that the stories follow the INVEST principle (Independent, Negotiable, Valuable, Estimable, Small, and Testable)."
      },
      {
        taskId: 102,
        taskName: "prioritization",
        taskLabel: "Prioritization",
        prompt: "As a Product Owner, your task is to prioritize user stories based on business value, dependencies, and stakeholder needs. Use prioritization frameworks like MoSCoW or WSJF to justify ranking."
      }
    ],
    default_icon: "📊"
  },
  {
    id: 2,
    name: "Solution Architect",
    role: "SA",
    tasks: [
      {
        taskId: 201,
        taskName: "user_story_generation",
        taskLabel: "User Story Generation",
        prompt: "As a Solution Architect, your task is to generate user stories that capture architectural decisions, trade-offs, and system constraints while ensuring alignment with business goals."
      },
      {
        taskId: 202,
        taskName: "prioritization",
        taskLabel: "Prioritization",
        prompt: "As a Solution Architect, your task is to prioritize architectural components and decisions based on scalability, security, and maintainability considerations."
      }
    ],
    default_icon: "🏗️"
  },
  {
    id: 3,
    name: "Quality Assurance",
    role: "QA",
    tasks: [
      {
        taskId: 301,
        taskName: "user_story_generation",
        taskLabel: "User Story Generation",
        prompt: "As a Quality Assurance expert, your task is to generate detailed test cases and acceptance criteria based on the given user stories to ensure comprehensive test coverage."
      },
      {
        taskId: 302,
        taskName: "prioritization",
        taskLabel: "Prioritization",
        prompt: "As a Quality Assurance expert, your task is to prioritize test scenarios and automation efforts based on risk, critical functionality, and defect history."
      }
    ],
    default_icon: "✅"
  },
  {
    id: 4,
    name: "Developer",
    role: "developer",
    tasks: [
      {
        taskId: 401,
        taskName: "user_story_generation",
        taskLabel: "User Story Generation",
        prompt: "As a Developer, your task is to refine user stories by adding technical details, defining acceptance criteria, and breaking down stories into manageable development tasks."
      },
      {
        taskId: 402,
        taskName: "prioritization",
        taskLabel: "Prioritization",
        prompt: "As a Developer, your task is to prioritize development tasks based on dependencies, complexity, and potential impact on project timelines."
      }
    ],
    default_icon: "💻"
  },
  {
    id: 5,
    name: "Compliance Agent",
    role: "Compliance",
    tasks: [
      {
        taskId: 501,
        taskName: "user_story_generation",
        taskLabel: "User Story Generation",
        prompt: "As a Compliance Agent, your task is to generate compliance-related user stories that address regulatory requirements such as GDPR, HIPAA, and industry best practices."
      },
      {
        taskId: 502,
        taskName: "prioritization",
        taskLabel: "Prioritization",
        prompt: "As a Compliance Agent, your task is to prioritize compliance tasks and reviews based on legal risk, business impact, and industry regulations."
      }
    ],
    default_icon: "⚖️"
  },
  {
    id: 6,
    name: "Security Expert",
    role: "Security",
    tasks: [
      {
        taskId: 601,
        taskName: "user_story_generation",
        taskLabel: "User Story Generation",
        prompt: "As a Security Expert, your task is to generate security-related user stories focusing on threat modeling, vulnerability mitigation, and secure coding practices."
      },
      {
        taskId: 602,
        taskName: "prioritization",
        taskLabel: "Prioritization",
        prompt: "As a Security Expert, your task is to prioritize security enhancements and vulnerability fixes based on threat severity, exploitability, and business risk."
      }
    ],
    default_icon: "🔐"
  }
];

export default personasWithTasks;
