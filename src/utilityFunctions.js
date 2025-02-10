import poIcon from "./assets/po.png";
import saIcon from "./assets/SA.png";
import developerIcon from "./assets/developer.png";
import finalIcon from "./assets/final.png";
import qaIcon from "./assets/qa.png";
import caIcon from "./assets/ca.png";
import seIcon from "./assets/se.png";
import defaultIcon from "./assets/default.png";
export const getChatMessageClass = (agentType) => {
    switch (agentType) {
      case "PO":
        return "chat-message-right";
      case "SA":
        return "chat-message-left";
      case "Developer":
        return "chat-message-center";
      case "QA":
        return "chat-message-center-1";
      case "Compliance":
        return "chat-message-center-2";
      case "Security":
        return "chat-message-center-3";
      case "Final Prioritization":
        return "chat-message-final";
      default:
        return "default-chat-message";
    }
  };

 export const handleSuccessResponse = (prioritizationTechnique, selectModel) => {
    // Check if browser supports speech synthesis
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(`Agents Chatting about ${prioritizationTechnique} technique using ${selectModel} model in Process`);
      window.speechSynthesis.speak(utterance);
    } else {
      console.log('Text-to-speech not supported.');
    }
  };

  export const addKeyToResponse = (responseData) => {
    if (!Array.isArray(responseData)) {
      return []; // Return an empty array if response data is not an array
    }
    return responseData.map((item, index) => ({
      ...item,
      key: index, // Assigning index as the key
    }));
  };

  export const getAgentImage = (agentType) => {
    switch (agentType) {
      case "PO":
        return poIcon;
      case "SA":
        return saIcon;
      case "Developer":
        return developerIcon;
      case "QA":
        return qaIcon;
      case "Compliance":
        return caIcon;
      case "Security":
        return seIcon;
      case "Final Prioritization":
        return finalIcon;
      default:
        return defaultIcon;
    }
  };
  

  export const labelOptions = [
    {
      value: "100_DOLLAR",
      label: "100 Dollar",
    },
    {
      value: "WSJF",
      label: "WSJF (Weighted Shortest Job First)",
    },
    {
      value: "MOSCOW",
      label: "MoSCoW (Must have, Should have, Could have, Won't have)",
    },
    {
      value: "KANO",
      label: "KANO (Customer Satisfaction)",
    },
    {
      value: "AHP",
      label: "AHP (Analytic Hierarchy Process)",
    },
  ];