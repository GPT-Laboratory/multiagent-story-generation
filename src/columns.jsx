import React from "react";

export const columns = [
  {
    title: "No",
    dataIndex: "index",
    key: "index",
    width: 80,
    render: (text, record, index) => index + 1, // Renders the row number
  },
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
    width: 400,
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
    width: 700,
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
    width: 600,
  },
  {
    title: "Suggested By",
    dataIndex: "suggestion",
    key: "suggestion",
    width: 200,
  },
  {
    title: "modification",
    dataIndex: "status",
    key: "status",
    width: 130,
  },

];

export const frameworkColumns = [
  {
    title: "No",
    dataIndex: "index",
    key: "index",
    width: 80,
    render: (text, record, index) => index + 1, // Renders the row number
  },
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
    width: 400,
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
    width: 700,
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
    width: 600,
  },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
    width: 200,
  },
  {
    title: "Compliance",
    dataIndex: "compliance",
    key: "compliance",
    width: 150,
    render: (compliance) => compliance ? "true" : "false",
  },
  {
    title: "Issues",
    dataIndex: "issues",
    key: "issues",
    width: 500,
  },
];


export const prioritizedColumns = [
  {
    title: "No",
    dataIndex: "index",
    key: "index",
    width: 80,
    render: (text, record, index) => index + 1, // Renders the row number
  },
  {
    title: "Old No",
    dataIndex: "ID",
    key: "ID",
    width: 80,
  },
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
    width: 500,
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
    width: 700,
  },
];

export const finalOutputColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
  // {
  //   title: "Number",
  //   dataIndex: "number",
  //   key: "number",
  // },
  // {
  //   title: "Status",
  //   dataIndex: "status",
  //   key: "status",
  // },
  {
    title: "Key",
    dataIndex: "key",
    key: "key",
  },
  {
    title: "Dollar Allocation",
    dataIndex: "dollar_allocation",
    key: "dollar_allocation",
  },
];


export const wsjfColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
  {
    title: "Business Value (BV)",
    dataIndex: "bv",
    key: "BV",
  },
  {
    title: "Time Criticality (TC)",
    dataIndex: "tc",
    key: "TC",
  },
  {
    title: "Risk Reduction/Opportunity Enablement (RR/OE)",
    dataIndex: "oe",
    key: "RR/OE",
  },
  {
    title: "Job Size (JS)",
    dataIndex: "js",
    key: "JS",
  },
  {
    title: "WSJF Score",
    dataIndex: "wsjf_score",
    key: "wsjf_score",
  },
];

export const wsmColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
  {
    title: "Business Value (BV)",
    dataIndex: "bv",
    key: "BV",
  },
  {
    title: "Feasibility (F)",
    dataIndex: "rc",
    key: "F",
  },
  {
    title: "Strategic Alignment (SA)",
    dataIndex: "sa",
    key: "SA",
  },
  {
    title: "Risk & Compliance (RC)",
    dataIndex: "rc",
    key: "RC",
  },
  {
    title: "Scalability (S)",
    dataIndex: "s",
    key: "S",
  },
  {
    title: "WSM Score",
    dataIndex: "wsm_score",
    key: "wsm_score",
  },
];


// Define columns for MoSCoW prioritization
export const moscowColumns = [
  {
    title: "No",
    dataIndex: "index",
    key: "index",
    width: 80,
    render: (text, record, index) => index + 1, // Renders the row number
  },
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
    width: 500,
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
    width: 700,
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
    width: 600,
  },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
    width: 90,
  },
  {
    title: "MoSCoW Priority",
    dataIndex: "moscow_category",
    key: "moscow_category",
    width: 150,
    render: (text) => {
      switch (text) {
        case 'M':
          return 'Must Have';
        case 'S':
          return 'Should Have';
        case 'C':
          return 'Could Have';
        case 'W':
          return "Won't Have";
      
        default:
          return text;
      }
    },
  },
];

export const kanoColumns = [
  {
    title: "No",
    dataIndex: "index",
    key: "index",
    width: 80,
    render: (text, record, index) => index + 1, // Renders the row number
  },
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
    width: 500,
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
    width: 700,
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
    width: 600,
  },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
    width: 90,
  },
  {
    title: "KANO Category",
    dataIndex: "kano_category",
    key: "kano_category",
    width: 150,
    render: (text) => {
      switch (text) {
        case 'B':
          return 'Basic Needs';
        case 'P':
          return 'Performance Needs';
        case 'E':
          return 'Excitement Needs';
        case 'I':
          return 'Indifferent';
        case 'R':
          return 'Reverse';
        default:
          return text;
      }
    },
  },
];

export const ahpColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
  {
    title: "Business Value (BV)",
    dataIndex: "BV",
    key: "BV",
  },
  {
    title: "Effort Required (ER)",
    dataIndex: "ER",
    key: "ER",
  },
  {
    title: "Dependencies (D)",
    dataIndex: "D",
    key: "D",
  },
  {
    title: "Weight (W)",
    dataIndex: "W",
    key: "W",
  },
  {
    title: "Overall Score (OS)",
    dataIndex: "OS",
    key: "OS",
  },
];


// Define columns for your table
export const testCasesColumns = [
  {
    title: "Test Case Suite No",
    dataIndex: "suite_number",
    key: "suite_number",
    width: 120,
  },
  {
    title: "Scenario",
    dataIndex: "scenario",
    key: "scenario",
  },
  {
    title: "Input",
    dataIndex: "input",
    key: "input",
  },
  {
    title: "Expected Output",
    dataIndex: "expected_output",
    key: "expected_output",
  },
];


export const bestPOStoriesColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Priority Points",
    dataIndex: "dollar_allocation",
    key: "dollar_allocation"
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
];

export const bestSAStoriesColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Priority Points",
    dataIndex: "priority_points",
    key: "priority_points"
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
];

export const bestDevStoriesColumns = [
  {
    title: "Category",
    dataIndex: "epic",
    key: "epic",
  },
  {
    title: "Requirement",
    dataIndex: "user_story",
    key: "user_story",
  },
  {
    title: "Priority Points",
    dataIndex: "priority_points",
    key: "priority_points"
  },
  {
    title: "Description",
    dataIndex: "description",
    key: "description",
  },
];
