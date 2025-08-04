import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import "./ChatStyle.css";
import { RQicon } from "./mysvg";
import { useNavigate, useLocation, useParams, Link, redirect } from "react-router-dom";
import { Content, Footer, Header } from "antd/es/layout/layout";
import { SearchOutlined, CaretRightOutlined, DownOutlined, DownloadOutlined, GlobalOutlined } from "@ant-design/icons";
import FullPageLoader from "./FullPageLoader";
import {
	columns,
	finalOutputColumns,
	wsjfColumns,
	moscowColumns,
	kanoColumns,
	ahpColumns,
	frameworkColumns,
	bestPOStoriesColumns,
	bestSAStoriesColumns,
	bestDevStoriesColumns,
	wsmColumns,
} from "./columns"; // Import the necessary columns
import TextArea from "antd/es/input/TextArea";
const { Panel } = Collapse;
import {
	Button,
	Form,
	Input,
	Layout,
	Space,
	Table,
	notification,
	Select,
	Collapse,
	Breadcrumb,
	Checkbox,
	List,
	Radio,
	Menu,
	Dropdown,
} from "antd";
import {
	addKeyToResponse,
	getAgentImage,
	getChatMessageClass,
	handleSuccessResponse,
	labelOptions,
	llmModels,
} from "./utilityFunctions";
import { downloadCSV, downloadPRD, handleDownloadReport } from "./helper/DownloadFile";
// import { getSocket } from "./SocketInstance";
// const WS_URL = "ws://localhost:8000/api/ws-chat";
import { socketURL } from "./SocketInstance.jsx";
import AddItem from "./AddItem.jsx";
import { getUserId } from "./components/GetLoginUserId.jsx";
import { useDispatch, useSelector } from "react-redux";
import { fetchFinalPrioritization, fetchFinalTablePrioritization, fetchProjects, fetchUserStories, setUserStorySelected } from "./features/MainSlice.jsx";
import { setResult1, updateItem, addItem, deleteItem, removeApprovedStory, addApprovedStory, approveAllStories } from "./features/TableStoriesResponse.jsx";
import DocxViewer from "./components/DocxViewer.jsx";
import { fetchAllReports } from "./features/ReportSlice.jsx";

// import personasWithTasks from "./helper/Persona.jsx";


const WS_URL = `${socketURL}/api/ws-chat`;


const toTitleCase = (str) => {
	return str
		.toLowerCase()
		.split(" ")
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(" ");
};


const App = ({ }) => {
	const { id } = useParams(); // Get ID from URL
	const dispatch = useDispatch();

	const [dataResponse, setDataResponse] = useState([])

	const [personasWithTasks, setPersonasWithTasks] = useState([])
	// const [projects, setProjects] = useState([]);
	// const [userStories, setUserStories] = useState([]);
	const [selectedVersion, setSelectedVersion] = useState(null);
	const result1 = useSelector((state) => state.tablestoriesresponse.result1);
	const approvedStories = useSelector((state) => state.tablestoriesresponse.approvedStories);



	const agentOptions = personasWithTasks.map((persona) => ({
		value: persona.role,
		// label: persona.name,
	}));
	const { projects, userStories, user_story_selected, prioritization, prioritization_response } = useSelector((state) => state.main);
	const { reports } = useSelector((state) => state.reports);

	console.log("reports data ", reports);





	console.log("user_story_selected", user_story_selected);
	console.log("userStories phiirr", userStories);



	// const selectedUserStory = userStories.find(story => story._id === user_story_selected);
	const selectedUserStory =
		userStories.find(story => story._id === user_story_selected) ||
		userStories.find(story => story.stories.some(s => s._id === user_story_selected));

	const [addNewItem, setAddNewItem] = useState(false);
	const [bestStoriesSelection, setBestStoriesSelection] = useState(false)
	const [requestId, setRequestId] = useState("");
	const [loading, setLoading] = useState(false);
	const [displayChatBox, setDisplayChatBox] = useState(false);
	const [ws, setWs] = useState(null);
	const [fileContent, setFileContent] = useState("");
	const [name, setName] = useState(
		"The proposed system is designed to streamline research processes by offering a suite of advanced features. It enables users to generate research-specific questions, interact through a React-based user interface, and choose between ChatGPT 3.5 or 4 for language modeling. The system supports API integration, adheres to specific inclusion and exclusion criteria for literature review, and facilitates paper summarization and data extraction. It also allows for both qualitative and quantitative analysis, directly addresses research queries, and aids in the production of key research documentation such as abstracts, introductions, and LaTeX summaries. This comprehensive tool aims to enhance research efficiency and output quality through its multifunctional capabilities."
	);
	const [textBox, setTextBox] = useState({
		vision:
			"Our vision is to transform our IT company into a leading, AI-enabled organization that leverages cutting‐edge artificial intelligence to optimize processes, empower data‐driven decision making, and deliver exceptional value to our stakeholders. By implementing a stakeholder-driven, LLM-powered multi-agent approach to requirements analysis for each AI adoption use case, we will ensure that every AI solution not only addresses real business challenges but also evolves with our dynamic market and technological landscape. Explanation of the Statement 1. Value Orientation: The statement emphasizes delivering “exceptional value” and “optimizing processes” so that AI adoption is seen as a means to achieve tangible business benefits rather than an end in itself. 2. Stakeholder Focus: It commits to “empowering data‐driven decision making” and addressing “real business challenges,” ensuring that the needs and expectations of customers, employees, and partners are at the heart of the initiative. 3. Shared Understanding and System Context: By mentioning the use of a “systematic, stakeholder-focused, and validated requirements engineering approach,” the statement reinforces the importance of a common understanding among all project participants. It implies that requirements will be gathered, clarified, and continuously refined based on both internal insights and market dynamics. 4. Problem–Requirement–Solution Separation: The vision makes it clear that AI is not adopted merely for technology’s sake. Instead, it’s a strategic tool designed to tackle defined challenges (“real business challenges”) and to support sustainable growth within our operational context. 5. Evolution and Continuous Improvement: The phrase “evolves with our dynamic market and technological landscape” captures the principle that requirements—and consequently our AI solutions—will change over time and need to be managed systematically.",
		mvp: "Minimum Viable Plan (MVP) for AI-Enabled Organizational Transformation 1. Vision Statement Transform our IT company into a leading AI- enabled organization that leverages cutting - edge artificial intelligence to optimize processes, empower data - driven decision - making, and deliver exceptional value to stakeholders. 2. Strategic Objectives .Establish a structured AI adoption framework to guide investment in AI technologies. .Develop a stakeholder - driven AI requirements process to ensure business alignment. .Implement AI governance, compliance, and ethical frameworks. .Define a roadmap for scalable AI integration across business units. .Foster a culture of AI - driven innovation and continuous learning. 3. Stakeholders & Their Goals .Executives: Ensure AI initiatives align with long - term business strategies. .IT Leaders: Develop scalable AI infrastructure and deployment capabilities. .Data Scientists: Optimize AI model development and operational integration. .Compliance Officers: Establish AI governance policies and ensure regulatory adherence. .Business Units: Leverage AI for decision intelligence and process automation. 4. MVP Scope(Initial Phase) .Deploy a stakeholder - driven, LLM - powered multi - agent system for AI use case analysis. .Identify and prioritize AI adoption initiatives using structured evaluation criteria. .Develop AI governance policies and ethical guidelines. .Establish an AI strategy roadmap for phased implementation.= 5. Success Metrics .Strategic AI Integration Index: Number of AI - driven decision - making processes incorporated into business operations. .AI Governance Readiness Score: Compliance with ethical AI policies and governance frameworks. .Business Impact Metrics: Improvement in AI - enabled decision - making at the executive level. .Scalability Readiness: Ability to expand AI use cases across multiple business units. 6. Iterative Roadmap Phase 1: Stakeholder - Driven AI Requirements Elicitation. .Engage key stakeholders in AI transformation planning. .Deploy LLM agents for AI requirements gathering and prioritization. .Validate AI adoption priorities with business leaders. Phase 2: AI Feasibility Assessment and Prioritization. .Assess technical, financial, and operational feasibility of AI initiatives. .Rank initiatives based on business impact, risk, and readiness. .Develop pilot plans for the top - priority AI projects. Phase 3: AI Governance and Initial Implementation. .Establish AI governance, compliance, and ethical frameworks. .Implement AI solutions in selected business areas. .Monitor performance metrics and collect stakeholder feedback. Phase 4: Continuous AI Scaling and Evaluation. .Expand AI initiatives across additional business units. .Implement iterative improvements based on usage data and feedback. .Develop AI talent and foster partnerships with AI research institutions. 7. Expected Outcomes .A structured AI adoption framework aligned with business strategy. .Increased operational efficiency through AI - driven process optimization. .Enhanced data - driven decision - making capabilities. .Robust AI governance and compliance mechanisms. .Scalable AI initiatives that evolve with business needs.",

		// "The glossary serves as a reference for key terms used within the Mobile Delivery Application to ensure users have a clear understanding of its features. For instance, Preparation refers to the stage where delivery items are scanned, organized, and scheduled. Delivery Status indicates real-time updates on a package’s journey, while Accounting covers the recording and reconciliation of delivery data for accountability. Additionally, Real-Time Tracking is a feature that allows continuous monitoring of delivery progress to enhance transparency and efficiency",
		user_analysis:
			""
		// "The User Analysis focuses on understanding the needs and behaviors of postal workers to tailor the Mobile Delivery Application to their workflow. The primary users are postal workers responsible for managing deliveries, routes, and package updates. Their key requirements include maintaining accuracy in delivery records, receiving real-time updates, and having access to a user-friendly interface. The application addresses challenges such as reducing manual errors, saving time, and streamlining workflows. Regular feedback from users is incorporated into the development process to continuously refine and enhance the application's functionality.",
	});
	const [feedback, setFeedBack] = useState(null);
	const [feedback1, setFeedBack1] = useState("");
	const [showFeedBack, setShowFeedBack] = useState(false);
	const [num_stories, setNoOfRequirments] = useState(10);
	const [selectType, setSelectType] = useState("input");
	const [type, setType] = useState("textbox");
	const [isApproved, setIsApproved] = useState(false)
	const [prioritizationTechnique, setPrioritizationTechnique] =
		useState("100_Dollar");
	const [selectModel, setSelectModel] = useState("gpt-4o-mini");
	const [rounds, setRounds] = useState(3);
	const [frameWork, setFromWork] = useState("INVEST framework");
	const [frameWorkResult, setFrameWorkResult] = useState([]);
	const [selectedFile, setSelectedFile] = useState(null);
	const [visionFile, setVisionFile] = useState(null);
	const [mvpFile, setMvpFile] = useState(null);
	const location = useLocation();
	const navigate = useNavigate();
	const [percentages, setPercentages] = useState({
		po: 50,
		sa: 25,
		dev: 25,
	});
	const [finalTableData, setFinalTableData] = useState([]);
	const [bestPORounds, setbestPORounds] = useState([]);
	const [bestDevRounds, setbestDevRounds] = useState([]);
	const [bestSARounds, setbestSARounds] = useState([]);
	const [finalPrioritizationType, setFinalPrioritizationType] = useState("");
	const chatContainerRef = useRef(null);
	const [messageQueue, setMessageQueue] = useState([]);
	const [prioritizationResponses, setPrioritizationResponses] = useState([])
	const [isDisplayingMessage, setIsDisplayingMessage] = useState(false);
	const [responses, setResponses] = useState({
		PO: [],
		QA: [],
		developer: [],
		"Final Prioritization": [],
	});
	const textAreaRefs = useRef({});
	const handleModel = (value) => {
		setSelectModel(value);
	};
	const handleframe = (value) => {
		setFromWork(value);
	};
	const handleLanguage = (value) => {
		setPrioritizationTechnique(value);
	};
	const [messageSequence, setMessageSequence] = useState([]);
	const [totalMessageData, setTotalMessageData] = useState("");

	const [selectedRowKeys, setSelectedRowKeys] = useState([]);

	// const [agent1, setAgent1] = useState("Product Owner");
	// const [agent2, setAgent2] = useState("Solution Architect");
	// const [agent3, setAgent3] = useState("developer");
	const [agent1, setAgent1] = useState("");
	const [agent2, setAgent2] = useState("");
	const [agent3, setAgent3] = useState("");
	const [new_version, setNewVersion] = useState(false);
	const project = projects.find((project) => project.id === id);
	const [fileId, setFileId] = useState(null);
	const [reportFeedback, setReportFeedback] = useState(`Executive summary 
 Key Insights from the MVP & Vision: 
Scope,Challenges, Requirments , cateogries of  prioritization , Roadmap & Prioritization, Summary of User story generation, and prirotization, and which agents involves in this project.
	  `);



	// Handle row selection
	const onSelectChange = (newSelectedRowKeys) => {
		setSelectedRowKeys(newSelectedRowKeys);
		console.log("Selected row keys:", newSelectedRowKeys);
	};


	// Configure row selection
	const rowSelection = {
		selectedRowKeys,
		onChange: onSelectChange,
	};
	// const [selectedInnerPanel, setSelectedInnerPanel] = useState([]);
	const [selectedInnerPanel, setSelectedInnerPanel] = useState({
		productOwner: null,
		solutionArchitect: null,
		developer: null,
	});

	const [sortedInfo, setSortedInfo] = useState({});

	const handleSort = (order) => {
		const sortedData = [...result1].sort((a, b) => {
			if (order === "ascend") {
				return a.epic > b.epic ? 1 : -1; // Sort by "epic" in ascending order
			} else {
				return a.epic < b.epic ? 1 : -1; // Sort by "epic" in descending order
			}
		});
		setSortedInfo({ order });
		// Update your state with sorted data (assuming you have a state setter for result1)
		// setResult1(sortedData);
		dispatch(setResult1(sortedData));
	};

	const menu = (
		<Menu>
			<Menu.Item onClick={() => handleSort("ascend")}>Category (Ascending)</Menu.Item>
			<Menu.Item onClick={() => handleSort("descend")}>Category (Descending)</Menu.Item>
		</Menu>
	);


	const handleClearUpload = () => {
		dispatch(setResult1([]));; // Set result to empty array
		setTextBox({
			vision:
				"Our vision is to transform our IT company into a leading, AI-enabled organization that leverages cutting‐edge artificial intelligence to optimize processes, empower data‐driven decision making, and deliver exceptional value to our stakeholders. By implementing a stakeholder-driven, LLM-powered multi-agent approach to requirements analysis for each AI adoption use case, we will ensure that every AI solution not only addresses real business challenges but also evolves with our dynamic market and technological landscape. Explanation of the Statement 1. Value Orientation: The statement emphasizes delivering “exceptional value” and “optimizing processes” so that AI adoption is seen as a means to achieve tangible business benefits rather than an end in itself. 2. Stakeholder Focus: It commits to “empowering data‐driven decision making” and addressing “real business challenges,” ensuring that the needs and expectations of customers, employees, and partners are at the heart of the initiative. 3. Shared Understanding and System Context: By mentioning the use of a “systematic, stakeholder-focused, and validated requirements engineering approach,” the statement reinforces the importance of a common understanding among all project participants. It implies that requirements will be gathered, clarified, and continuously refined based on both internal insights and market dynamics. 4. Problem–Requirement–Solution Separation: The vision makes it clear that AI is not adopted merely for technology’s sake. Instead, it’s a strategic tool designed to tackle defined challenges (“real business challenges”) and to support sustainable growth within our operational context. 5. Evolution and Continuous Improvement: The phrase “evolves with our dynamic market and technological landscape” captures the principle that requirements—and consequently our AI solutions—will change over time and need to be managed systematically.",
			mvp: "Minimum Viable Plan (MVP) for AI-Enabled Organizational Transformation 1. Vision Statement Transform our IT company into a leading AI- enabled organization that leverages cutting - edge artificial intelligence to optimize processes, empower data - driven decision - making, and deliver exceptional value to stakeholders. 2. Strategic Objectives .Establish a structured AI adoption framework to guide investment in AI technologies. .Develop a stakeholder - driven AI requirements process to ensure business alignment. .Implement AI governance, compliance, and ethical frameworks. .Define a roadmap for scalable AI integration across business units. .Foster a culture of AI - driven innovation and continuous learning. 3. Stakeholders & Their Goals .Executives: Ensure AI initiatives align with long - term business strategies. .IT Leaders: Develop scalable AI infrastructure and deployment capabilities. .Data Scientists: Optimize AI model development and operational integration. .Compliance Officers: Establish AI governance policies and ensure regulatory adherence. .Business Units: Leverage AI for decision intelligence and process automation. 4. MVP Scope(Initial Phase) .Deploy a stakeholder - driven, LLM - powered multi - agent system for AI use case analysis. .Identify and prioritize AI adoption initiatives using structured evaluation criteria. .Develop AI governance policies and ethical guidelines. .Establish an AI strategy roadmap for phased implementation.= 5. Success Metrics .Strategic AI Integration Index: Number of AI - driven decision - making processes incorporated into business operations. .AI Governance Readiness Score: Compliance with ethical AI policies and governance frameworks. .Business Impact Metrics: Improvement in AI - enabled decision - making at the executive level. .Scalability Readiness: Ability to expand AI use cases across multiple business units. 6. Iterative Roadmap Phase 1: Stakeholder - Driven AI Requirements Elicitation. .Engage key stakeholders in AI transformation planning. .Deploy LLM agents for AI requirements gathering and prioritization. .Validate AI adoption priorities with business leaders. Phase 2: AI Feasibility Assessment and Prioritization. .Assess technical, financial, and operational feasibility of AI initiatives. .Rank initiatives based on business impact, risk, and readiness. .Develop pilot plans for the top - priority AI projects. Phase 3: AI Governance and Initial Implementation. .Establish AI governance, compliance, and ethical frameworks. .Implement AI solutions in selected business areas. .Monitor performance metrics and collect stakeholder feedback. Phase 4: Continuous AI Scaling and Evaluation. .Expand AI initiatives across additional business units. .Implement iterative improvements based on usage data and feedback. .Develop AI talent and foster partnerships with AI research institutions. 7. Expected Outcomes .A structured AI adoption framework aligned with business strategy. .Increased operational efficiency through AI - driven process optimization. .Enhanced data - driven decision - making capabilities. .Robust AI governance and compliance mechanisms. .Scalable AI initiatives that evolve with business needs.",

			user_analysis: "",
		});
		setSelectModel("gpt-4o-mini");
		setAgent1("AI Strategist");
		setAgent2("Business Process Owner");
		setAgent3("Security Expert");
	};

	const handleUpload = () => {


		// console.log("Updated Filtered Story with Key:", updatedFilteredStory);

		const updatedFilteredStory = addKeyToResponse(selectedUserStory.stories)

		// Dispatch the updated filteredStory to setResult1
		dispatch(setResult1(updatedFilteredStory));
		// dispatch(setResult1(updatedFilteredStory)).then(() => {
		// 	dispatch(fetchFinalTablePrioritization(user_story_selected));
		// });

		dispatch(fetchFinalTablePrioritization(user_story_selected));

		dispatch(fetchFinalPrioritization(user_story_selected));

		dispatch(fetchAllReports(selectedUserStory?._id))




		// setFileId(reports.file_id)



		// dispatch(setResult1(selectedUserStory.stories));

		setTextBox({
			vision: selectedUserStory.vision,
			mvp: selectedUserStory.mvp,

			user_analysis: "",
		});
		setSelectModel(selectedUserStory.model);
		console.log("for agents:", selectedUserStory.agents);

		setAgent1(selectedUserStory.agents[0]?.role || "AI Strategist");
		setAgent2(selectedUserStory.agents[1]?.role || "Business Process Owner");
		setAgent3(selectedUserStory.agents[2]?.role || "Security Expert");
	};

	const handleVersionChange = (value) => {
		if (selectedVersion === value) {
			setSelectedVersion(null); // Deselect if clicking the selected version again
		} else {
			setSelectedVersion(value);
		}
	};

	useEffect(() => {
		// if (prioritization.length > 0) {
		setDisplayChatBox(true);
		// setIsDisplayingMessage(true)
		console.log(prioritization.message);
		setFinalTableData(prioritization.message)
		setFinalPrioritizationType(prioritization.prioritization_type)
		// }
	}, [prioritization])



	useEffect(() => {
		if (reports.length > 0) {
			setFileId(reports[0].file_id)
			console.log("comes", reports[0].file_id);
		}

	}, [reports])

	console.log(" prioritization_response", messageSequence);




	console.log("finalTableData result", finalTableData);


	useEffect(() => {
		if (userStories.length > 0 && dataResponse.length > 0) {
			const filteredStory = userStories.find(
				(story) => story.stories.some((s) => s._id === dataResponse[0]._id)
			);
			console.log("Filtered Story:", filteredStory);

			if (filteredStory) {
				e.log("Updated Filtered Story with Key:", updatedFilteredStory);

				const updatedFilteredStory = addKeyToResponse(filteredStory.stories)

				// Dispatch the updated filteredStory to setResult1
				dispatch(setResult1(updatedFilteredStory));
			}
		}
	}, [userStories]); // Runs when `userStories` updates



	// const fetchProjects = async () => {
	// 	setLoading(true);
	// 	const userId = getUserId(); // Get logged-in user ID
	// 	if (!userId) {
	// 		message.error("User not logged in");
	// 		setLoading(false);
	// 		return;
	// 	}

	// 	try {
	// 		const response = await fetch(`/api/projects?user_id=${userId}`);
	// 		const data = await response.json();
	// 		setProjects(data);
	// 	} catch (error) {
	// 		message.error("Failed to fetch projects");
	// 	}
	// 	setLoading(false);
	// };

	// useEffect(() => {
	// 	fetchProjects();
	// }, []);


	useEffect(() => {
		if (selectedUserStory) {
			// handleUpload(); // Call/ handleUpload when a valid story is selected
			// setNewVersion(false)
			setTimeout(() => {
				handleUpload();
			}, 100);
		} else {
			handleClearUpload(); // Call handleClearUpload when no story is selected
		}
	}, [selectedUserStory]); // Runs whenever selectedUserStory changes

	useEffect(() => {
		if (result1.length > 0) {
			setNewVersion(false)
		}

	}, [result1])

	useEffect(() => {
		dispatch(fetchProjects());
		dispatch(fetchUserStories());
	}, [dispatch]);


	const handleAgentChange = (value, setter, otherAgents) => {
		if (!otherAgents.includes(value)) {
			setter(value);
		}
	};

	const selectedAgents = [agent1, agent2, agent3];

	const isButtonDisabled =
		!selectedInnerPanel.productOwner ||
		!selectedInnerPanel.solutionArchitect ||
		!selectedInnerPanel.developer;

	// const handleCheckboxChange = (key) => {
	// 	setSelectedInnerPanel(key);
	// };

	useEffect(() => {
		const fetchPersonas = async () => {
			try {
				const response = await fetch(`/api/personas/${id}`); // Send project_id
				const data = await response.json();
				setPersonasWithTasks(data);
			} catch (error) {
				console.error("Error fetching personas:", error);
			}
		};

		// const fetchUserStories = async () => {
		// 	try {
		// 		const response = await fetch(`/api/user_stories/${id}`); // Fetch user stories
		// 		const data = await response.json();
		// 		if (response.ok) {
		// 			setUserStories(data || []);
		// 		} else {
		// 			console.warn("No user stories found.");
		// 		}
		// 	} catch (error) {
		// 		console.error("Error fetching user stories:", error);
		// 	}
		// };

		fetchPersonas();
		// fetchUserStories();
	}, []);
	useEffect(() => {
		console.log("userstores comes", userStories);
	}, [userStories]);


	useEffect(() => {
		console.log("selected rounds:", selectedInnerPanel);

	}, [selectedInnerPanel])

	const handleCheckboxChange = (mainKey, key, data) => {
		setSelectedInnerPanel((prev) => ({
			...prev,
			[mainKey]: {
				key,
				data,
			},
		}));
	};




	const handleInputChange = (role, value) => {
		const numericValue = parseInt(value, 10) || 0;
		const otherRoles = ["po", "sa", "dev"].filter((r) => r !== role);

		const otherTotal = percentages[otherRoles[0]] + percentages[otherRoles[1]];

		if (numericValue <= 100 && numericValue >= 0) {
			const remaining = 100 - numericValue;

			const updatedPercentages = {
				[otherRoles[0]]: Math.round((percentages[otherRoles[0]] / otherTotal) * remaining),
				[otherRoles[1]]: Math.round((percentages[otherRoles[1]] / otherTotal) * remaining),
				[role]: numericValue,
			};

			setPercentages(updatedPercentages);
		}
	};


	useEffect(() => {
		const connectWebSocket = () => {
			const socket = new WebSocket(WS_URL);
			const handleMessage = (event) => {
				console.log("event data:", event.data);
				const data = JSON.parse(event.data);

				if (data.agentType === "Final_output_into_table") {
					setLoading(false);
					setFinalTableData(data.message);
					setFinalPrioritizationType(data.prioritization_type);
				}

				if (data.agentType === "Best product owner rounds") {
					setbestPORounds(data.message);
				}

				if (data.agentType === "Best solution architect rounds") {
					setbestSARounds(data.message);
				}

				if (data.agentType === "Best developer rounds") {
					setbestDevRounds(data.message);
				}

				if (data.message.trim().length > 0) {
					setMessageQueue((prevQueue) => [
						...prevQueue,
						{ agentType: data.agentType, message: data.message },
					]);
					setTotalMessageData((prvMessage) => prvMessage + " " + data?.message);
					setPrioritizationResponses((prevQueue) => [
						...prevQueue,
						{ agentType: data.agentType, message: data.message },
					]);
				}
				setLoading(false);
			};
			const requestId = `${Date.now()}-${Math.floor(Math.random() * 1000000)}`; // Generate unique ID
			setRequestId(requestId);

			socket.onopen = () => {
				console.log("WebSocket connected");
				socket.send(JSON.stringify({ request_id: requestId })); // Send the requestId to the server
				setLoading(false);
			};
			socket.onmessage = handleMessage;
			socket.onerror = (error) => {
				console.error("WebSocket error:", error);
				setLoading(false);
			};
			socket.onclose = (event) => {
				console.log("WebSocket disconnected", event);
				setLoading(false);
				// Try to reconnect after a delay
				setTimeout(() => {
					console.log("Attempting to reconnect...");
					connectWebSocket();
				}, 5000);
			};
			setWs(socket);
			return () => {
				socket.close();
				console.log("WebSocket closed");
			};
		};

		connectWebSocket();
	}, []);

	const handleCopyClick = () => {
		navigator.clipboard
			.writeText(totalMessageData)
			.then(() => {
				notification.success({
					message: "Content Copied Successfully",
				});
			})
			.catch((err) => {
				alert("Failed to copy: ", err);
			});
	};

	const displayMessage = (agentType, message) => {
		return new Promise((resolve) => {
			let index = 0;
			const batchSize = 6; // Number of characters to display per interval

			const intervalId = setInterval(() => {
				if (index < message.length) {
					setMessageSequence((prevSequence) => {
						const lastMessageIndex = prevSequence.findIndex(
							(msg) => msg.agentType === agentType && !msg.completed
						);

						if (lastMessageIndex > -1) {
							// Update the existing message with more characters
							const updatedSequence = [...prevSequence];
							updatedSequence[lastMessageIndex] = {
								...updatedSequence[lastMessageIndex],
								message: message.slice(0, index + batchSize),
							};
							return updatedSequence;
						} else {
							// Add a new message entry for the new message
							return [
								...prevSequence,
								{
									agentType,
									message: message.slice(0, index + batchSize),
									completed: false,
								},
							];
						}
					});
					index += batchSize;
				} else {
					clearInterval(intervalId);
					setMessageSequence((prevSequence) => {
						const updatedSequence = [...prevSequence];
						const lastMessageIndex = updatedSequence.findIndex(
							(msg) => msg.agentType === agentType && !msg.completed
						);
						if (lastMessageIndex > -1) {
							updatedSequence[lastMessageIndex].completed = true; // Mark the message as completed
						}
						return updatedSequence;
					});
					resolve(); // Resolve the promise when the message is fully displayed
				}
			}, 10); // Adjust the interval duration as needed
		});
	};

	useEffect(() => {
		const recentAgentType =
			messageSequence[messageSequence.length - 1]?.agentType;
		if (recentAgentType && textAreaRefs.current[recentAgentType]) {
			const textArea = textAreaRefs.current[recentAgentType];
			textArea.focus();
			textArea.scrollTop = textArea.scrollHeight;
		}
		if (chatContainerRef.current) {
			chatContainerRef.current.scrollTop =
				chatContainerRef.current.scrollHeight;
			chatContainerRef.current.focus();
		}
	}, [messageSequence]);

	useEffect(() => {
		console.log("total messages:", totalMessageData);
	}, [totalMessageData]);
	useEffect(() => {
		const processMessageQueue = async () => {
			if (messageQueue.length > 0 && !isDisplayingMessage) {
				setIsDisplayingMessage(true);
				const nextMessage = messageQueue[0];
				await displayMessage(nextMessage.agentType, nextMessage.message);
				setMessageQueue((prevQueue) => prevQueue.slice(1));
				if (nextMessage.agentType === "Final Prioritization") {
					setTimeout(() => {
						setIsDisplayingMessage(false);
						setTimeout(() => {
							chatContainerRef.current.scrollTop =
								chatContainerRef.current.scrollHeight;
							chatContainerRef.current.focus();
						}, [200]);
					}, [1000]);
				} else {
					setIsDisplayingMessage(false);
				}
			}
		};
		processMessageQueue();
	}, [messageQueue, isDisplayingMessage]);

	const handleMvpFileChange = (e) => {
		setMvpFile(e.target.files[0]);
	};

	const handleVisionFileChange = (e) => {
		// console.log(e.target.files);

		setVisionFile(e.target.files[0]);
	};

	const handleReset = (e) => {
		e.preventDefault();
		dispatch(setResult1([]));
		setIsApproved(false)
	}

	const handleApproveStories = (e) => {
		dispatch(approveAllStories(result1));
		setIsApproved(true)
		console.log("approved stories", approvedStories);

	}

	const handleGenerateStoriesByFiles = async (e) => {
		e.preventDefault();

		// Validate files before submitting
		if (!visionFile || !mvpFile) {
			notification.error({
				message: "Please upload Vision and MVP files",
			});
			return;
		}

		try {
			setLoading(true);
			setShowFeedBack(true);
			// Create a FormData object to handle file uploads
			const formData = new FormData();
			formData.append("vision_file", visionFile);
			formData.append("mvp_file", mvpFile);
			formData.append("model", selectModel);
			formData.append("feedback", feedback1); // Add feedback

			console.log("form data: ", formData);
			console.log("vision file: ", visionFile);
			console.log("mvp file: ", mvpFile);
			console.log("feedback: ", feedback1);

			const response = await fetch("/api/generate-user-stories-by-files", {
				method: "POST",
				body: formData,
			});

			if (!response.ok) {
				throw new Error("Failed to upload files");
			}

			const data = await response.json();
			console.log("Backend response:", data);

			// Assuming the response contains 'stories_with_epics'
			const responseDataWithKeys = addKeyToResponse(data.stories_with_epics);
			console.log("uploaded data: ", responseDataWithKeys);
			// setResult1(responseDataWithKeys);
			dispatch(setResult1(responseDataWithKeys));

			setLoading(false);
			notification.success({
				message: "File uploaded successfully.",
			});
		} catch (error) {
			console.error("Error submitting data:", error);
			setLoading(false);
			notification.error({
				message: "Internal Server Error: " + error.message, // Display the error message
			});
		}
	};
	// for docx
	// const handleProjectReport = async (e) => {
	// 	e.preventDefault();
	// 	const selectedAgents = [agent1, agent2, agent3].map(role =>
	// 		personasWithTasks.find(persona => persona.role === role)
	// 	);
	// 	const agentsData = selectedAgents.map(agent => ({
	// 		role: agent.role,
	// 	}));

	// 	try {
	// 		setLoading(true);
	// 		const response = await fetch("/api/create-project-report-docx", {
	// 			method: "POST",
	// 			headers: {
	// 				"Content-Type": "application/json",
	// 			},
	// 			body: JSON.stringify({
	// 				request_id: requestId,
	// 				project_id: id,
	// 				project_title: project?.project_name,
	// 				vision: textBox.vision,
	// 				mvp: textBox.mvp,
	// 				glossary: textBox.glossary,
	// 				user_analysis: textBox.user_analysis,
	// 				model: selectModel,
	// 				feedback: feedback,
	// 				agents: agentsData,
	// 				prioritized_stories: finalTableData,
	// 				selectedUserStory: selectedUserStory?._id
	// 			}),
	// 		});

	// 		if (!response.ok) {
	// 			throw new Error("Failed to generate report");
	// 		}

	// 		// Handle the DOCX response
	// 		const blob = await response.blob();
	// 		const url = window.URL.createObjectURL(blob);
	// 		const a = document.createElement("a");
	// 		a.href = url;
	// 		a.download = `${project?.project_name.replace(/ /g, "_")}.docx`;
	// 		document.body.appendChild(a);
	// 		a.click();
	// 		document.body.removeChild(a);
	// 		window.URL.revokeObjectURL(url);

	// 		setLoading(false);
	// 		notification.success({
	// 			message: "Project Report Successfully Created and Downloaded",
	// 		});
	// 	} catch (error) {
	// 		console.error("Error submitting data:", error);
	// 		setLoading(false);
	// 		notification.error({
	// 			message: "Failed to Generate Report",
	// 			description: error.message || "An error occurred while generating the report.",
	// 		});
	// 	}
	// };

	const handleProjectReport = async (e) => {
		e.preventDefault();
		const selectedAgents = [agent1, agent2, agent3].map(role =>
			personasWithTasks.find(persona => persona.role === role)
		);
		const agentsData = selectedAgents.map(agent => ({
			role: agent.role,
		}));

		try {
			setLoading(true);
			const response = await fetch("/api/create-project-report-docx", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					request_id: requestId,
					project_id: id,
					project_title: project?.project_name,
					vision: textBox.vision,
					mvp: textBox.mvp,
					user_analysis: textBox.user_analysis,
					model: selectModel,
					feedback: reportFeedback,
					agents: agentsData,
					prioritized_stories: finalTableData,
					selectedUserStory: selectedUserStory?._id,
					prioritizationResponses: prioritizationResponses
				}),
			});

			if (!response.ok) {
				throw new Error("Failed to generate report");
			}

			const result = await response.json();
			console.log("Report created:", result);

			setFileId(result.file_id); // Store file_id
			console.log(fileId);

			dispatch(fetchAllReports(selectedUserStory?._id))


			notification.success({
				message: "Project Report Successfully Created",
				description: `Report Title: ${result.title}`,
			});

			setLoading(false);
			// Optionally, update the UI to show the newly created report
		} catch (error) {
			console.error("Error submitting data:", error);
			setLoading(false);
			notification.error({
				message: "Failed to Generate Report",
				description: error.message || "An error occurred while generating the report.",
			});
		}
	};




	// for pdf

	// const handleProjectReport = async (e) => {
	// 	e.preventDefault();

	// 	// Extract selected agents' data
	// 	const selectedAgents = [agent1, agent2, agent3].map(role =>
	// 		personasWithTasks.find(persona => persona.role === role)
	// 	);

	// 	const agentsData = selectedAgents.map(agent => ({
	// 		role: agent?.role || "Unknown Role",
	// 	}));

	// 	try {
	// 		setLoading(true);

	// 		const response = await fetch("/api/create-project-report-pdf", {
	// 			method: "POST",
	// 			headers: {
	// 				"Content-Type": "application/json",
	// 			},
	// 			body: JSON.stringify({
	// 				request_id: requestId,
	// 				project_id: id,
	// 				project_title: project?.project_name || "Untitled Project",
	// 				vision: textBox.vision || "No vision provided",
	// 				mvp: textBox.mvp || "No MVP provided",
	// 				glossary: textBox.glossary || "No glossary available",
	// 				user_analysis: textBox.user_analysis || "No user analysis available",
	// 				model: selectModel,
	// 				feedback: feedback || "No feedback provided",
	// 				agents: agentsData,
	// 				prioritized_stories: finalTableData || [],
	// 			}),
	// 		});

	// 		if (!response.ok) {
	// 			throw new Error("Failed to generate report");
	// 		}

	// 		// Handle the PDF response
	// 		const blob = await response.blob();
	// 		const url = window.URL.createObjectURL(blob);

	// 		// Create a temporary download link
	// 		const a = document.createElement("a");
	// 		a.href = url;
	// 		a.download = `${project?.project_name?.replace(/ /g, "_") || "Project_Report"}.pdf`;
	// 		document.body.appendChild(a);
	// 		a.click();
	// 		document.body.removeChild(a);
	// 		window.URL.revokeObjectURL(url);

	// 		setLoading(false);
	// 		notification.success({
	// 			message: "Success",
	// 			description: "Project Report Successfully Created and Downloaded",
	// 		});
	// 	} catch (error) {
	// 		console.error("Error generating project report:", error);
	// 		setLoading(false);
	// 		notification.error({
	// 			message: "Failed to Generate Report",
	// 			description: error.message || "An error occurred while generating the report.",
	// 		});
	// 	}
	// };




	const handleGenerateStories = async (e) => {
		console.log("vision text: ", textBox.vision);
		console.log("mvp text: ", textBox.mvp);

		console.log("user analysis text: ", textBox.user_analysis);

		e.preventDefault();
		const selectedAgents = [agent1, agent2, agent3].map(role =>
			personasWithTasks.find(persona => persona.role === role)
		);
		console.log(selectedAgents[0].role);

		// const agentsData = selectedAgents.map(agent => ({
		// 	role: agent.role,
		// }));

		const agentsData = selectedAgents
			.filter(agent => agent !== undefined) // Filter out undefined agents
			.map(agent => ({
				role: agent.role,
			}));

		console.log("agentdtaatt", agentsData);
		// return;


		let imageBase64 = null;
		if (visionFile) {
			const reader = new FileReader();
			reader.readAsDataURL(visionFile);
			reader.onload = () => {
				imageBase64 = reader.result.split(",")[1]; // Remove data:image/png;base64 prefix
			};
			await new Promise(resolve => reader.onloadend = resolve);
		}
		if (visionFile) {
			const reader = new FileReader();
			reader.readAsDataURL(visionFile);
			reader.onload = () => {
				imageBase64 = reader.result.split(",")[1]; // Remove data:image/png;base64 prefix
			};
			await new Promise(resolve => reader.onloadend = resolve);
		}

		try {
			setLoading(true);
			const response = await fetch("/api/generate-user-stories", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},

				body: JSON.stringify({
					// objective: name,
					request_id: requestId,
					project_id: id,
					vision: textBox.vision,
					mvp: textBox.mvp,
					user_analysis: textBox.user_analysis,
					model: selectModel,
					feedback: feedback,
					context_image: imageBase64,
					agents: agentsData,
					new_version: new_version,
					selectedUserStory: selectedUserStory?._id
				}),
			});
			if (!response.ok) {
				throw new Error("Response");
			}
			const message = await response.json();
			console.log("generated stories:", message);
			let dataResponse = message.final_response;
			// dispatch(fetchUserStories()); // Ensure Redux state updates before filtering

			// dispatch(setUserStorySelected(dataResponse[0]._id))

			dispatch(fetchUserStories()).then(() => {
				dispatch(setUserStorySelected(dataResponse[0]._id));
			});

			setLoading(false);
			notification.success({
				message: "User stories Generated",
			});
		} catch (error) {
			console.error("Error submitting data:", error);
			setLoading(false);
			notification.error({
				message: "Internal Server Error",
			});
		}
	};

	const handleReGenerateStories = async (e) => {

		const agentsData = selectedAgents.map(agent => ({
			// name: agent.role,
			role: agent.role,
			// prioritization: agent.tasks.find(task => task.taskName === "prioritization").prompt
		}));


		e.preventDefault();
		// const requestId = `${Date.now()}-${Math.floor(Math.random() * 1000000)}`; // Same logic for consistency

		try {
			setLoading(true);
			const response = await fetch("/api/regenerate-user-stories", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					// objective: name,
					// request_id: requestId,
					// generated_stories: result1,
					// model: selectModel,
					// feedback: feedback,
					// agents: agentsData,

					request_id: requestId,
					project_id: id,
					generated_stories: result1,
					vision: textBox.vision,
					mvp: textBox.mvp,
					user_analysis: textBox.user_analysis,
					model: selectModel,
					feedback: feedback,
					// context_image: imageBase64,
					agents: agentsData,
					selectedUserStory: selectedUserStory?._id
				}),
			});
			if (!response.ok) {
				throw new Error("Response");
			}
			const message = await response.json();
			// console.log("generated stories:", message);
			// let dataResponse = message.final_response
			// 	.map((i, index) => ({
			// 		...i,
			// 		key: index,
			// 	}));

			// setResult1(dataResponse);

			console.log("generated stories:", message);
			let dataResponse = message.final_response;
			// dispatch(fetchUserStories()); // Ensure Redux state updates before filtering

			// dispatch(setUserStorySelected(dataResponse[0]._id))

			dispatch(fetchUserStories()).then(() => {
				dispatch(setUserStorySelected(dataResponse[0]._id));
			});

			// console.log(dataResponse);
			setLoading(false);
			notification.success({
				message: "User stories Generated",
			});
		} catch (error) {
			console.error("Error submitting data:", error);
			setLoading(false);
			notification.error({
				message: "Internal Server Error",
			});
		}
	};


	const handleFileUpload = async (file) => {
		// console.log(selectedFile);
		try {
			setLoading(true);
			const formData = new FormData();
			formData.append("file", selectedFile);
			formData.append("project_id", id)
			const response = await fetch("/api/upload-csv", {
				method: "POST",
				body: formData,
			});
			if (!response.ok) {
				throw new Error("Failed to upload file");
			}
			const data = await response.json();
			// console.log(data);
			const responseDataWithKeys = addKeyToResponse(data.stories_with_epics);
			console.log("Uploaded file data:", responseDataWithKeys); // Log the transformed data
			// setResult1(responseDataWithKeys);
			dispatch(fetchUserStories()).then(() => {
				dispatch(setUserStorySelected(responseDataWithKeys[0]._id));
			});
			// dispatch(setResult1(responseDataWithKeys));

			setLoading(false);
			notification.success({
				message: "File uploaded successfully",
			});
		} catch (error) {
			console.error("Error uploading file:", error);
			setLoading(false);
			notification.error({
				message: "Error uploading file",
			});
		}
	};
	const handleFrameWork = async (e) => {
		e.preventDefault();
		try {
			setLoading(true);
			const response = await fetch("/api/check-user-stories-quality", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					framework: frameWork, // Ensure 'name' has a valid string value
					stories: result1, // Ensure 'num_stories' has a valid number value
					model: selectModel,
				}),
			});
			if (!response.ok) {
				throw new Error("Response");
			}
			const message = await response.json();
			// console.log(message);
			let dataResponse = message.stories_with_epics.map((i, index) => ({
				...i,
				key: index,
			}));
			setFrameWorkResult(dataResponse);
			console.log(dataResponse);
			setLoading(false);
			notification.success({
				message: "Framework User stories Generated",
			});
		} catch (error) {
			console.error("Error submitting data:", error);
			setLoading(false);
			notification.error({
				message: "Internal Server Error",
			});
		}
	};

	useEffect(() => {
		if (location.state?.updatedItem) {
			const updatedItem = location.state.updatedItem;


			// setResult1((prevResult) => {
			// 	// If prevResult is empty but we have an updatedItem,
			// 	// create a new array with just that item
			// 	if (prevResult.length === 0) {
			// 		return [updatedItem];
			// 	}
			// 	// Otherwise update the existing array
			// 	return prevResult.map((item) =>
			// 		item.key === updatedItem.key ? updatedItem : item
			// 	);
			// });
			dispatch(updateItem(updatedItem));


			// Clear the location state
			navigate("/", { replace: true });
			console.log("updatedItem: ", updatedItem);
			console.log("result1: ", result1);
		}
	}, [location.state, navigate]);

	// const handleDelete = (record) => {
	// 	// setResult1((prevResult) =>
	// 	// 	prevResult.filter((item) => item.key !== record.key)
	// 	// );
	// 	dispatch(deleteItem(record._id));

	// 	console.log("Deleted:", record);
	// };

	const handleDelete = async (record) => {
		try {
			await dispatch(deleteItem(record._id)).unwrap(); // Ensures delete is completed
			console.log("Deleted:", record);
		} catch (error) {
			console.error("Error deleting story:", error);
		}
	};



	const [approvedData, setApprovedData] = useState([]);
	console.log(approvedData);

	const handleApprove = (record) => {
		const isAlreadyApproved = approvedData.some((item) => item._id === record._id); // Check if the row is already approved

		if (isAlreadyApproved) {
			// If already approved, remove it from the state
			setApprovedData((prevData) => prevData.filter((item) => item._id !== record._id));
			dispatch(removeApprovedStory(record));
		} else {
			// If not approved, add it to the state
			setApprovedData((prevData) => [...prevData, record]);
			dispatch(addApprovedStory(record))
			console.log("approvedStories", approvedStories);
		}
	};

	const handleRemoveStory = (record) => {
		
			// If already approved, remove it from the state
			setApprovedData((prevData) => prevData.filter((item) => item._id !== record._id));
			dispatch(removeApprovedStory(record));
	
	};

	const handleEdit = (record) => {
		console.log("record comes", record);

		const recordId = record._id ? record._id : record.key;

		navigate(`/edit/${id}/${recordId}`, { state: { item: record } });
	};



	const handleAdd = () => {
		navigate(`/add`);
	};


	// const handleUpdateItem = (updatedItem) => {
	//   setResult1((prevResult) =>
	//     prevResult.map((item) =>
	//       item.key === updatedItem.key ? updatedItem : item
	//     )
	//   );
	// };
	const sendInput = () => {
		if (ws && ws.readyState === WebSocket.OPEN) {
			// console.log("technique:", prioritizationTechnique);
			const selectedAgents = [agent1, agent2, agent3].map(role =>
				personasWithTasks.find(persona => persona.role === role)
			);

			// Prepare agent data to send
			// const agentsData = selectedAgents.map(agent => ({
			// 	name: agent.name,
			// 	role: agent.role,
			// 	basic_user_prompt: agent.basic_user_prompt
			// }));
			const agentsData = selectedAgents.map(agent => ({
				name: agent.name,
				role: agent.role,
				prioritization: agent.tasks.find(task => task.taskName === "prioritization").prompt
			}));

			if (selectType === "input") {
				ws.send(
					JSON.stringify({
						stories: approvedStories,
						visions: textBox.vision,
						mvps: textBox.mvp,
						model: selectModel,
						prioritization_type: prioritizationTechnique,
						feedback: feedback,
						rounds: rounds,
						agents: agentsData,
						project_id: id
					})
				);
			} else {
				ws.send(
					JSON.stringify({
						stories: result1,
						model: selectModel,
						prioritization_type: prioritizationTechnique,
						feedback: feedback,
						rounds: rounds,
						agents: agentsData,
						project_id: id
					})
				);
			}
		}
	};
	const handleSubmit = async (e) => {
		setBestStoriesSelection(true)
		e.preventDefault();
		setMessageSequence([]);
		setDisplayChatBox(true);
		setLoading(true);
		sendInput();
		setTotalMessageData("");
		handleSuccessResponse(prioritizationTechnique, selectModel);
		notification.success({
			message: "Successfully ",
		});
		
	};

	const sendInputData = () => {
		if (ws && ws.readyState === WebSocket.OPEN) {
			// console.log("technique:", prioritizationTechnique);
			ws.send(
				JSON.stringify({
					stories: approvedStories,
					model: selectModel,
					prioritization_type: prioritizationTechnique,
					selected_panels: {
						productOwner: selectedInnerPanel.productOwner?.data || null,
						solutionArchitect: selectedInnerPanel.solutionArchitect?.data || null,
						developer: selectedInnerPanel.developer?.data || null,
					},
					selected_weights: {
						po: percentages.po,
						sa: percentages.sa,
						dev: percentages.dev,
					},
					finalPrioritization: true,
					story_id: selectedUserStory?._id,

					// feedback: feedback,
				})
			);
		}
	};
	const handleFinalPrioritization = async (e) => {
		e.preventDefault();
		// setMessageSequence([]);
		// setDisplayChatBox(true);
		// setMessageSequence([]);
		setMessageSequence((prev) => prev.filter((entry) => entry.agentType !== "Final Prioritization"));
		setMessageQueue([])
		setLoading(true);
		sendInputData();
		setTotalMessageData("");
		setFinalTableData([]);
		// handleSuccessResponse(prioritizationTechnique, selectModel);
		dispatch(fetchAllReports(selectedUserStory?._id));
		notification.success({
			message: "Successfully ",
		});
	};



	const renderChatMessages = () => {
		const agentMessages = messageSequence.reduce((acc, entry) => {
			const { agentType, message } = entry;
			if (agentType !== "Final Prioritization" && agentType !== "error") {
				if (!acc[agentType]) {
					acc[agentType] = [];
				}
				acc[agentType].push(message);
			}
			return acc;
		}, {});


		let finalMessage = messageSequence.reduce((acc, entry) => {
			const { agentType, message } = entry;
			if (agentType === "Final Prioritization") {
				if (!acc[agentType]) {
					acc[agentType] = [];
				}
				acc[agentType].push(message);
			}
			return acc;
		}, {});





		return (
			<>
				<div
					className="chat-container"
					ref={chatContainerRef}
					style={{
						margin: "0 auto",
						padding: "20px 15px",
						overflowY: "auto",
						display: "flex",
						flexDirection: "column",
					}}>
					<div
						className="chat-messages-row"
						style={{
							display: "flex",
							flexDirection: "row",
							flexWrap: "wrap",
							justifyContent: "space-between",
							width: "100%",
						}}>
						{Object.entries(agentMessages).map(([agentType, messages]) => (
							<div
								key={agentType}
								id={agentType}
								className="chat-box"
								style={{
									flexDirection: "column",
									display: "flex",
									width: "32.5%",
								}}>
								<div
									className="chat-message"
									style={{ flexDirection: "column", alignItems: "center" }}>
									<div className="profile">
										<img
											src={getAgentImage(agentType)}
											alt={agentType}
										/>
									</div>
									<div>{agentType}</div>
								</div>
								<div
									className={`message-content ${getChatMessageClass(
										agentType
									)}`}>
									<TextArea
										key={`${agentType}-textarea`}
										ref={(el) => (textAreaRefs.current[agentType] = el)}
										className="message-content"
										value={messages.join("\n")}
										autoSize={{ minRows: 2 }}
										readOnly
									/>
								</div>
							</div>
						))}
					</div>

					{/* adding Collapse */}

					{/* Add collapses here */}

					{bestStoriesSelection &&
						<>
							<Collapse
								expandIcon={({ isActive }) => (
									<CaretRightOutlined rotate={isActive ? 90 : 0} />
								)}
								accordion={false}
								defaultActiveKey={["1"]}
								style={{
									marginTop: "20px",
									marginBottom: "16px",

								}}>
								<Panel
									header={
										<>
											{`${agent1}`}
										</>
									}
									key="1">
									<Collapse
										expandIcon={({ isActive }) => (
											<CaretRightOutlined rotate={isActive ? 90 : 0} />
										)}
										accordion={false}
										defaultActiveKey={["1-1"]}
										style={{
											marginTop: "10px",
										}}
									>
										<Panel
											header={<>
												<input
													type="checkbox"
													// checked={selectedInnerPanel === "1-1"}
													// onChange={() => handleCheckboxChange("1-1")}
													checked={selectedInnerPanel.productOwner?.key === "1-1"}
													onChange={() => handleCheckboxChange("productOwner", "1-1", bestPORounds.round_one)}
													style={{ marginRight: "10px" }}
												/>

												round 1</>}
											key="1-1"
										>
											<div
												style={{
													display: "flex",
													// width: "78vw",
													gap: "10px",
													marginBottom: "6px",
												}}
											>

												<Table
													// rowSelection={rowSelection}
													dataSource={bestPORounds.round_one}
													columns={bestPOStoriesColumns}
													pagination={false}
													scroll={{ x: 1200, y: 500 }}
												/>



											</div>
										</Panel>
										<Panel
											header={<>
												<input
													type="checkbox"
													checked={selectedInnerPanel.productOwner?.key === "1-2"}
													onChange={() => handleCheckboxChange("productOwner", "1-2", bestPORounds.round_two)}
													style={{ marginRight: "10px" }}
												/>
												round 2</>}
											key="1-2"
										>
											<div
												style={{
													display: "flex",
													// width: "78vw",
													gap: "10px",
													marginBottom: "6px",
												}}
											>
												<Table
													// rowSelection={rowSelection}
													dataSource={bestPORounds.round_two}
													columns={bestPOStoriesColumns}
													pagination={false}
													scroll={{ x: 1200, y: 500 }}
												/>
											</div>
										</Panel>
									</Collapse>
								</Panel>

								<Panel
									header={
										<>
											{`${agent2}`}
										</>
									}
									key="2">
									<Collapse
										expandIcon={({ isActive }) => (
											<CaretRightOutlined rotate={isActive ? 90 : 0} />
										)}
										accordion={false}
										defaultActiveKey={["2-1"]}
										style={{
											marginTop: "10px",
										}}
									>
										<Panel
											header={<>
												<input
													type="checkbox"
													checked={selectedInnerPanel.solutionArchitect?.key === "2-1"}
													onChange={() => handleCheckboxChange("solutionArchitect", "2-1", bestSARounds.round_one)}
													style={{ marginRight: "10px" }}
												/>
												round 1</>}
											key="2-1"
										>
											<div
												style={{
													display: "flex",
													// width: "78vw",
													gap: "10px",
													marginBottom: "6px",
												}}
											>

												<Table
													// rowSelection={rowSelection}
													dataSource={bestSARounds.round_one}
													columns={bestPOStoriesColumns}
													pagination={false}
													scroll={{ x: 1200, y: 500 }}
												/>



											</div>
										</Panel>
										<Panel
											header={<>
												<input
													type="checkbox"
													cchecked={selectedInnerPanel.solutionArchitect?.key === "2-2"}
													onChange={() => handleCheckboxChange("solutionArchitect", "2-2", bestSARounds.round_two)}
													style={{ marginRight: "10px" }}
												/>
												round 2</>}
											key="2-2"
										>
											<div
												style={{
													display: "flex",
													// width: "78vw",
													gap: "10px",
													marginBottom: "6px",
												}}
											>
												<Table
													// rowSelection={rowSelection}
													dataSource={bestSARounds.round_two}
													columns={bestPOStoriesColumns}
													pagination={false}
													scroll={{ x: 1200, y: 500 }}
												/>
											</div>
										</Panel>
									</Collapse>
								</Panel>

								<Panel
									header={
										<>

											{`${agent3}`}
										</>
									}
									key="3">
									<Collapse
										expandIcon={({ isActive }) => (
											<CaretRightOutlined rotate={isActive ? 90 : 0} />
										)}
										accordion={false}
										defaultActiveKey={["3-1"]}
										style={{
											marginTop: "10px",
										}}
									>
										<Panel
											header={<>
												<input
													type="checkbox"
													checked={selectedInnerPanel.developer?.key === "3-1"}
													onChange={() => handleCheckboxChange("developer", "3-1", bestDevRounds.round_one)}
													style={{ marginRight: "10px" }}
												/>
												round 1</>}
											key="3-1"
										>

											<div
												style={{
													display: "flex",
													// width: "78vw",
													gap: "10px",
													marginBottom: "6px",
												}}
											>

												<Table
													// rowSelection={rowSelection}
													dataSource={bestDevRounds.round_one}
													columns={bestPOStoriesColumns}
													pagination={false}
													scroll={{ x: 1200, y: 500 }}
												/>



											</div>
										</Panel>
										<Panel
											header={<>
												<input
													type="checkbox"
													checked={selectedInnerPanel.developer?.key === "3-2"}
													onChange={() => handleCheckboxChange("developer", "3-2", bestDevRounds.round_two)}
													style={{ marginRight: "10px" }}
												/>
												round 2</>}
											key="3-2"
										>
											<div
												style={{
													display: "flex",
													// width: "78vw",
													gap: "10px",
													marginBottom: "6px",
												}}
											>
												<Table
													// rowSelection={rowSelection}
													dataSource={bestDevRounds.round_two}
													columns={bestPOStoriesColumns}
													pagination={false}
													scroll={{ x: 1200, y: 500 }}
												/>
											</div>
										</Panel>
									</Collapse>
								</Panel>
							</Collapse>

							<Form
								layout="vertical"

								style={{ display: "flex", justifyContent: 'flex-end', alignItems: 'flex-end', gap: "10px", }}>
								{/* <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", width: "100%" }}> */}

								<Form.Item label={`${agent1}`} >
									<Input
										type="number"
										value={percentages.po}
										onChange={(e) => handleInputChange("po", e.target.value)}
										style={{ width: "130px", marginLeft: "5px" }}
									/>
								</Form.Item>

								<Form.Item label={`${agent2}`}>


									<Input
										type="number"
										value={percentages.sa}
										onChange={(e) => handleInputChange("sa", e.target.value)}
										style={{ width: "200px", marginLeft: "5px" }}
									/>
								</Form.Item>
								<Form.Item label={`${agent3}`}>


									<Input
										type="number"
										value={percentages.dev}
										onChange={(e) => handleInputChange("dev", e.target.value)}
										style={{ width: "150px", marginLeft: "5px" }}
									/>
								</Form.Item>
								{/* </div> */}
								<Form.Item  >

									<Button
										type="primary"
										// onClick={() => console.log("Final Prioritization Clicked")}
										onClick={handleFinalPrioritization}
										disabled={isButtonDisabled}

									>
										Final Prioritization
									</Button>
								</Form.Item>
							</Form>
						</>
					}


					{Object.entries(finalMessage).map(([agentType, messages]) => (
						<div
							key={agentType}
							id={agentType}
							className="chat-box"
							style={{
								flexDirection: "column",
								display: "flex",
								width: "100%",
							}}>
							<div
								className="chat-message"
								style={{ flexDirection: "column", alignItems: "center" }}>
								<div className="profile">
									<img
										src={getAgentImage(agentType)}
										alt={agentType}
									/>
								</div>
								<div>{agentType}</div>
							</div>
							<div
								className={`message-content ${getChatMessageClass(agentType)}`}>
								<TextArea
									key={`${agentType}-textarea`}
									ref={(el) => (textAreaRefs.current[agentType] = el)}
									className="message-content"
									value={messages.join("\n")}
									autoSize={{ minRows: 2 }}
									readOnly
								/>
							</div>
						</div>
					))}

					{/* {!isDisplayingMessage && finalTableData.length > 0 && ( */}
					{finalTableData?.length > 0 && (
						<>
							<div
								className="final-table-container"
								style={{ marginTop: "20px", width: "100%" }}>
								<button
									className="copy-button"
									onClick={handleCopyClick}>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										width="24"
										height="24"
										fill="none"
										viewBox="0 0 24 24"
										className="icon-sm">
										<path
											clipRule="evenodd"></path>
										fill="currentColor"
										fillRule="evenodd"
										d="M7 5a3 3 0 0 1 3-3h9a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3h-2v2a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3v-9a3 3 0 0 1 3-3h2zm2 2h5a3 3 0 0 1 3 3v5h2a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1h-9a1 1 0 0 0-1 1zM5 9a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h9a1 1 0 0 0 1-1v-9a1 1 0 0 0-1-1z"
									</svg>
									Copy
								</button>
								<h2>Final Prioritized Stories</h2>
								<Table
									dataSource={finalTableData}
									columns={
										finalPrioritizationType === "WSJF"
											? wsjfColumns
											: finalPrioritizationType === "MOSCOW"
												? moscowColumns
												: finalPrioritizationType === "100_DOLLAR"
													? finalOutputColumns
													: finalPrioritizationType === "WSM"
														? wsmColumns
														: finalPrioritizationType === "KANO"
															? kanoColumns
															: finalPrioritizationType === "AHP"
																? ahpColumns
																: ""
									}
									pagination={false}
									scroll={{ x: 1200, y: 500 }}
								/>
								<div style={{ display: 'flex', justifyContent: 'end', }}>
									<Button
										type="primary"
										style={{ width: '16%', marginTop: '20px' }}
										// icon={<SearchOutlined />}
										onClick={() => downloadCSV(finalTableData)}
									// onClick={()=> downloadPRD(finalTableData)}

									>
										Download Final Prioritization
									</Button>
								</div>
							</div>

							<div
								style={{
									width: "100%",
									border: "1px solid #ccc",
									padding: 10,
									borderRadius: "10px",
									margin: "20px 0px"
								}}>
								<Form
									layout="vertical"
									style={{
										width: "100%",
										display: "flex",
										alignItems: "center",
										justifyContent: "end",
									}}>

									<Form.Item
										label="Instructions"
										style={{ flex: "1 1 70%", marginRight: "5px" }}
									>
										<TextArea
											rows={2}
											placeholder="Write Instructions here..."
											value={reportFeedback}
											onChange={(e) => setReportFeedback(e.target.value)}
											style={{ width: "100%" }}
										// autoSize={{ minRows: 2 }}
										/>
									</Form.Item>


									<Form.Item
										label="Model"
										style={{ marginLeft: "10px", marginRight: "10px" }}>
										<Select
											placeholder="Select Model"
											optionFilterProp="children"
											onChange={handleModel}
											value={selectModel}
											defaultValue="gpt-4o-mini"
											options={llmModels}
										/>
									</Form.Item>
									<Form.Item
										style={{
											display: "flex",
											alignItems: "end",
											marginTop: "25px",
										}}>
										<Button
											type="primary"
											icon={<DownloadOutlined />}
											onClick={handleProjectReport}
										// onClick={()=> downloadPRD(datacomes)}
										>
											Create Report
										</Button>
									</Form.Item>
								</Form>
							</div>

							{/* <Button onClick={() => handleDownloadReport(selectedUserStory)}
								type="primary"

							>
								Get Report
							</Button> */}
							{/* {finalTableData.length > 0 &&
							<DocxViewer selectedUserStoryId={selectedUserStory}/>
							} */}
							{/* 
							{ fileId && <DocxViewer fileId={fileId} />}
							{ fileId && <DocxViewer fileId={fileId} />} */}
							{fileId && <DocxViewer key={fileId} fileId={fileId} />}





						</>
					)}

				</div>
			</>
		);
	};

	return (
		<>
			{/* {addNewItem && (

				<AddItem
					onUpdate={result1}
					isOpen={addNewItem}
					onClose={() => setAddNewItem(false)}
				/>
			)
			} */}
			<Layout>
				{/* <Header style={{ backgroundColor: "#f3fff3" }}>
					<div
						style={{
							display: "flex",
							flexDirection: "row",
							justifyContent: "space-between",
							marginLeft: "0px",
						}}>
						<div>
							<RQicon
								width={"60px"}
								height={"60px"}
							/>
						</div>
						<div style={{ fontSize: "20px", color: "black" }}>
							<strong>Multi-Agent GPT Prioritization Tool</strong>
						</div>
						<div></div>
					</div>
				</Header> */}
				<Layout>
					<Content>


						{loading && <FullPageLoader />}
						<div style={{
							display: ' flex',
						}}>
							<Breadcrumb style={{
								margin: '20px',
								marginLeft: '40px'
							}}>
								<Breadcrumb.Item><Link to="/">Projects List</Link></Breadcrumb.Item>
								<Breadcrumb.Item><Link  >Home Page</Link></Breadcrumb.Item>
								{/* <Breadcrumb.Item><Link to="/agent_list">Agents List</Link></Breadcrumb.Item> */}
							</Breadcrumb>


						</div>
						<div style={{
							// border:"1px solid",
							// margin:"2px auto"
						}}>
							{project ? <p style={{ fontSize: '16px', marginLeft: '52px', fontWeight: 'bold' }}>Project : {toTitleCase(project.project_name)}</p> : <p>Project not found</p>}
						</div>
						<div
							id="mainContainer"
							style={{
								lineHeight: "0px",
								display: "flex",
								flexDirection: "column",
								alignItems: "center",
								overflowY: "auto",
								height: "85vh",
								paddingBottom: "30px",
							}}>
							<Collapse
								expandIcon={({ isActive }) => (
									<CaretRightOutlined rotate={isActive ? 90 : 0} />
								)}
								accordion={false}
								defaultActiveKey={["1"]}
								style={{
									marginTop: "20px",
									marginBottom: "16px",
									width: "94vw",
								}}>
								<Panel
									header="Requirement Engineering Section"
									key="1"
									style={{}}>
									<div
										style={{
											display: "flex",
											widows: "78vw",
											gap: "10px",
											marginBottom: "6px",
										}}>
										<div
											style={{
												width: "20%",
												border: "1px solid #ccc",
												paddingLeft: 15,

												// paddingBottom: 15,
												borderRadius: "10px",
												marginBottom: 5,
											}}>
											<div
												style={{
													paddingBottom: 10,
												}}>
												<h5 style={{ marginTop: "8px" }}> Select Type:</h5>
												<div
													style={{
														marginTop: "-10px",
													}}>
													<input
														type="checkbox"
														checked={selectType === "input"}
														onChange={() => setSelectType("input")}
														style={{ marginRight: "10px", cursor: "pointer" }}
														id="input"
													/>
													<label
														htmlFor="input"
														style={{ cursor: "pointer" }}>
														Input Content
													</label>
												</div>
												<br />
												{
													!selectedUserStory &&
													<div
														style={{
															marginTop: "-15px",
														}}>
														<input
															type="checkbox"
															checked={selectType === "file"}
															onChange={() => setSelectType("file")}
															style={{ marginRight: "10px", cursor: "pointer" }}
															id="file"
														/>
														<label
															htmlFor="file"
															style={{ cursor: "pointer" }}>
															User stories uplaod
														</label>
													</div>
												}
											</div>
										</div>

										{selectType === "input" && (
											<div
												style={{
													width: "91vw",
													border: "1px solid #ccc",
													paddingLeft: 15,
													paddingRight: 15,
													marginBottom: 5,
													borderRadius: "10px",
												}}>
												<div>
													<h5>
														Hello, Enter your idea for generating user stories.
													</h5>
													<div
														style={{
															paddingBottom: 10,
															display: "flex",

														}}>
														{/* <h5 style={{ marginTop: "8px" }}> Select Type:</h5> */}
														<div
															style={{
																marginRight: "10px",
															}}>
															<input
																type="checkbox"
																checked={type === "textbox"}
																onChange={() => setType("textbox")}
																style={{ marginRight: "10px", cursor: "pointer" }}
																id="textbox"
															/>
															<label
																htmlFor="textbox"
																style={{ cursor: "pointer" }}>
																Textboxs
															</label>
														</div>
														<br />
														<div
														// style={{
														//   marginTop: "-15px",
														// }}
														>
															<input
																type="checkbox"
																checked={type === "vision_file"}
																onChange={() => setType("vision_file")}
																style={{ marginRight: "10px", cursor: "pointer" }}
																id="vision_file"
															/>
															<label
																htmlFor="vision_file"
																style={{ cursor: "pointer" }}>
																Upload files
															</label>
														</div>
														{type === "textbox" && (

															<div style={{
																display: "flex",
																justifyContent: "space-between",
																// border:'2px solid red',
																alignItems: "center",

																paddingLeft: "25px",
																width: '100%',
																// marginRight: "37px",
															}}>
																<div style={{
																	display: "flex",
																	justifyContent: "space-between",
																	// border:'2px solid red',
																	width: '50%',

																	alignItems: "center",

																}}>
																	<Form.Item label="Agent 1"
																		layout="vertical"

																	>
																		<Select
																			value={agent1}
																			onChange={(value) => handleAgentChange(value, setAgent1, [agent2, agent3])}
																			options={agentOptions.map((option) => ({
																				...option,
																				disabled: selectedAgents.includes(option.value) && option.value !== agent1,
																			}))}
																		/>
																	</Form.Item>

																	<Form.Item label="Agent 2"
																		layout="vertical"

																	>
																		<Select
																			value={agent2}
																			// style={{margin: "0px 5px"}}
																			onChange={(value) => handleAgentChange(value, setAgent2, [agent1, agent3])}
																			options={agentOptions.map((option) => ({
																				...option,
																				disabled: selectedAgents.includes(option.value) && option.value !== agent2,
																			}))}
																		/>
																	</Form.Item>

																	<Form.Item
																		layout="vertical"

																		label="Agent 3">
																		<Select
																			// style={{marginLeft: " 5px"}}


																			value={agent3}
																			onChange={(value) => handleAgentChange(value, setAgent3, [agent1, agent2])}
																			options={agentOptions.map((option) => ({
																				...option,
																				disabled: selectedAgents.includes(option.value) && option.value !== agent3,
																			}))}
																		/>
																	</Form.Item>
																</div>
																<Button type="primary" onClick={() => navigate(`/agent_list/${id}`)}>List Of Agents</Button>

																{/* {userStories.length > 0 && (
																	<Form.Item style={{ marginTop: "10px" }}>
																		<div
																			style={{
																				maxHeight: userStories.length > 2 ? "100px" : "auto", // Enable scrolling if more than 2
																				overflowY: userStories.length > 2 ? "auto" : "visible",
																				border: "1px solid #d9d9d9",
																				borderRadius: "5px",
																				padding: "5px",
																			}}
																		>
																			<List
																				bordered
																				size="small"
																				dataSource={userStories.map((_, index) => `Version-${index + 1}`)}
																				renderItem={(item) => <List.Item>{item}</List.Item>}
																			/>
																		</div>
																	</Form.Item>
																)} */}




															</div>
														)}
													</div>
												</div>
												{type === "textbox" ? (
													<div>
														<Form
															layout="vertical"
															style={{
																width: "100%",
																display: "flex",
																alignItems: "center",
															}}>
															<Form.Item
																label=" Vision Textbox"
																style={{ flex: "1 1 70%", marginRight: "5px" }}>
																<TextArea
																	rows={14}
																	placeholder="Enter your objective"
																	value={textBox.vision}
																	onChange={(e) =>
																		setTextBox({
																			...textBox,
																			vision: e.target.value,
																		})
																	}
																	style={{ color: "black" }}
																/>
															</Form.Item>
															<Form.Item
																label=" MVP Textbox"
																style={{ flex: "1 1 70%", marginRight: "5px" }}>
																<TextArea
																	rows={14}
																	placeholder="Enter your objective"
																	value={textBox.mvp}
																	onChange={(e) =>
																		setTextBox({
																			...textBox,
																			mvp: e.target.value,
																		})
																	}
																	style={{ color: "black" }}
																/>
															</Form.Item>



															<Form.Item
																label="Select Model"
																style={{ flex: "18%", marginRight: "5px" }}>
																<Select
																	placeholder="Select Framework"
																	optionFilterProp="children"
																	onChange={handleModel}
																	value={selectModel}
																	defaultValue="gpt-4o"
																	options={[
																		{
																			value: "gpt-3.5-turbo",
																			label: "GPT-3.5 Turbo",
																		},
																		{
																			value: "gpt-4o-mini",
																			label: "GPT-4o",
																		},
																		// {
																		// 	value: "deepseek/deepseek-r1-distill-llama-70b",
																		// 	label: "deepseek-r1"
																		// }
																	]}
																/>
															</Form.Item>

															{/* <Form.Item style={{ marginTop: "30px" }}>
																	<Button
																		type="primary"
																		icon={<SearchOutlined />}
																		disabled={result1.length > 0}

																		onClick={handleGenerateStories}>
																		Generate
																	</Button>
																</Form.Item> */}
															{result1.length > 0 || selectedUserStory ?
																<Form.Item style={{ marginTop: "95px" }}>
																	<Button
																		type="primary"
																		icon={<SearchOutlined />}
																		disabled={result1.length > 0 && !setNewVersion}
																		onClick={handleGenerateStories}
																	>
																		Generate
																	</Button>
																	{/* <Button
																		type="default"
																		icon={<GlobalOutlined />}  // Globe icon like in the image
																		shape="round"
																		style={{
																			marginTop: "12px",
																			display: "flex",
																			alignItems: "center",
																			justifyContent: "center",
																			border: "1px solid gray",
																			background: "transparent",
																			color: "",
																		}}
																	>
																		Search
																	</Button> */}
																	<Form.Item style={{ marginTop: "10px" }}>
																		<Checkbox
																			checked={new_version}
																			onChange={(e) => setNewVersion(e.target.checked)}
																		>
																			New Version
																		</Checkbox>
																	</Form.Item>
																</Form.Item> :
																<Form.Item style={{ marginTop: "30px" }}>
																	<Button
																		type="primary"
																		icon={<SearchOutlined />}
																		disabled={result1.length > 0}
																		onClick={handleGenerateStories}
																	>
																		Generate
																	</Button>
																	{/* <Button
																		type="default"
																		icon={<GlobalOutlined />}  // Globe icon like in the image
																		shape="round"
																		style={{
																			marginTop: "12px",
																			display: "flex",
																			alignItems: "center",
																			justifyContent: "center",
																			border: "1px solid gray",
																			background: "transparent",
																			color: "",
																		}}
																	>
																		Search
																	</Button> */}

																</Form.Item>
															}





														</Form>

														<div
															style={{
																width: "81%",

															}}
														>
															<Form
																layout="vertical"
																style={{
																	width: "100%",
																	display: "flex",
																	alignItems: "center",
																}}>
																{/*  */}
																<Form.Item
																	label=" User analysis Textbox"
																	style={{ flex: "1 1 70%", marginRight: "5px" }}>
																	<TextArea
																		rows={4}
																		placeholder="Enter your objective"
																		value={textBox.user_analysis}
																		onChange={(e) =>
																			setTextBox({
																				...textBox,
																				user_analysis: e.target.value,
																			})
																		}
																		style={{ color: "black" }}
																	/>
																</Form.Item>



															</Form>

															<Form.Item layout="vertical"
																label="Upload Context Image"
																style={{ flex: "1 1 70%", marginRight: "5px", width: '80%' }}>
																<Input
																	type="file"
																	name="vision"
																	onChange={handleVisionFileChange}
																/>
															</Form.Item>



														</div>
													</div>
												) : (
													<div>
														<Form
															layout="vertical"
															style={{
																width: "100%",
																display: "flex",
																alignItems: "center",
															}}>
															<Form.Item
																label="Upload Vision File"
																style={{ flex: "1 1 70%", marginRight: "5px" }}>
																<Input
																	type="file"
																	name="vision"
																	onChange={handleVisionFileChange}
																/>
															</Form.Item>
															<Form.Item
																label="Upload File"
																style={{ flex: "1 1 70%", marginRight: "5px" }}>
																<Input
																	type="file"
																	name="mvp"
																	onChange={handleMvpFileChange}
																/>
															</Form.Item>

															<Form.Item
																label="Select Model"
																style={{ flex: "18%", marginRight: "5px" }}>
																<Select
																	placeholder="Select Framework"
																	optionFilterProp="children"
																	onChange={handleModel}
																	value={selectModel}
																	defaultValue="gpt-4o"
																	options={[
																		{
																			value: "gpt-3.5-turbo",
																			label: "GPT-3.5 Turbo",
																		},
																		{
																			value: "gpt-4o-mini",
																			label: "GPT-4o",
																		},
																		// {
																		// 	value: "deepseek/deepseek-r1-distill-llama-70b",
																		// 	label: "deepseek-r1"
																		// }
																	]}
																/>
															</Form.Item>

															<Form.Item style={{ marginTop: "30px" }}>
																<Button
																	type="primary"
																	icon={<SearchOutlined />}
																	onClick={handleGenerateStoriesByFiles}>
																	Generate
																</Button>
															</Form.Item>
														</Form>
													</div>
												)}

												{result1.length > 0 && selectType === "input" && (
													<div
														style={{
															display: "flex",
															alignItems: "center",
															// border: "1px solid #ccc",
															marginTop: "-10px",
															// padding: 10,
															borderRadius: "10px",
															marginBottom: 10,
														}}>
														<Form
															layout="vertical"
															style={{
																width: "100%",
																display: "flex",
																alignItems: 'center',
																// alignContent: 'center',
																// border:'2px solid',

															}}>
															<Form.Item
																label="Feedback"
																style={{ flex: "1 1 70%", marginRight: "5px" }}
															>
																<TextArea
																	rows={4}
																	placeholder="Provide your feedback here..."
																	value={feedback}
																	onChange={(e) => setFeedBack(e.target.value)}
																	style={{ width: "100%" }}
																// autoSize={{ minRows: 2 }}
																/>
															</Form.Item>


															<Form.Item style={{ marginRight: "7px", marginTop: "25px" }}>
																<Button
																	type="primary"
																	icon={<SearchOutlined />}
																	onClick={handleReGenerateStories}>
																	Regenerate
																</Button>
															</Form.Item>

															<Form.Item style={{ marginTop: "25px" }}>
																<Button
																	type="primary"
																	// icon={<SearchOutlined />}
																	onClick={handleReset}>
																	Reset
																</Button>
															</Form.Item>

														</Form>
													</div>
												)}
											</div>
										)}

										{selectType === "file" && (
											<div
												style={{
													display: "flex",
													alignItems: "center",
													width: "81%",
													border: "1px solid #ccc",
													paddingRight: 15,
													paddingLeft: 15,
													marginBottom: 5,
													borderRadius: "10px",
												}}>
												<Form
													layout="vertical"
													style={{
														width: "100%",
														display: "flex",
														alignItems: "center",
													}}>
													<Form.Item
														label="Upload File"
														style={{ flex: 1, marginRight: "5px" }}>
														<Input
															type="file"
															onChange={(e) => setSelectedFile(e.target.files[0])}
														/>
													</Form.Item>
													<Form.Item style={{ marginBottom: "-4px" }}>
														<Button
															type="primary"
															onClick={() => {
																handleFileUpload();
															}}
															disabled={selectedFile === null}>
															Upload
														</Button>
													</Form.Item>
												</Form>
											</div>
										)}
									</div>

									{result1.length > 0 && selectType === "file" && (
										<div
											style={{
												display: "flex",
												alignItems: "center",
												border: "1px solid #ccc",
												padding: 10,
												borderRadius: "10px",
												marginBottom: 10,
											}}>
											<Form
												layout="vertical"
												style={{
													width: "100%",
													display: "flex",
													alignItems: "center",
												}}>
												<Form.Item
													label="Objective"
													style={{ flex: "1 1 70%", marginRight: "5px" }}>
													<TextArea
														rows={2}
														placeholder="Enter your objective"
														value={fileContent}
														onChange={(e) => setFileContent(e.target.value)}
														style={{ color: "black" }}
														autoSize={{ minRows: 2 }}
													/>
												</Form.Item>
											</Form>
										</div>
									)}
									{result1.length > 0 && showFeedBack && (
										<div
											style={{
												display: "flex",
												alignItems: "center",
												border: "1px solid #ccc",
												padding: 10,
												borderRadius: "10px",
												marginBottom: 10,
											}}>
											<Form
												layout="vertical"
												style={{
													width: "100%",
													display: "flex",
													alignItems: "center",
												}}>
												<Form.Item
													label="Feedback"
													style={{ flex: "1 1 70%", marginRight: "5px" }}>
													<TextArea
														rows={4}
														placeholder="Provide your feedback here..."
														value={feedback1}
														onChange={(e) => setFeedBack1(e.target.value)}
														style={{ width: "100%" }}
														autoSize={{ minRows: 2 }}
													/>
												</Form.Item>
												<Form.Item>
													<Button
														type="primary"
														style={{ marginTop: "25px" }}
														onClick={handleGenerateStoriesByFiles}>
														Submit
													</Button>
												</Form.Item>
											</Form>
										</div>
									)}
									{result1.length > 0 && (
										<div
											style={{
												display: "flex",
												flexDirection: 'column',
												alignItems: "end",
												border: "1px solid #ccc",
												padding: 10,
												borderRadius: "10px",
												marginBottom: 5,
											}}>

											<Space
												direction="vertical"
												style={{ width: "100%", padding: "10px 0px" }}>
												{/* <Table
													scroll={{ x: 1200, y: 500 }}
													style={{ width: "100%" }}
													dataSource={result1}
													columns={[
														...columns,
														{
															title: "Actions",
															key: "actions",
															render: (_, record) => (
																<div
																	style={{
																		display: "flex",
																		justifyContent: "space-between",
																		gap: "10px",
																	}}>

																	<button
																		onClick={() => handleApprove(record)} // Toggle approve
																		style={{
																			backgroundColor: isApprove ? "green" : "gray", // Change color based on approval status
																			color: "white",
																			padding: "5px 20px",
																			border: "none",
																			borderRadius: "5px",
																			cursor: "pointer",
																		}}
																	>
																		{isApproved ? "Approved" : "Approve"} 
																	</button>



																	<button
																		onClick={() => handleEdit(record)}
																		style={{
																			backgroundColor: "rgba(2, 130, 204, 0.74)",
																			color: "white",
																			padding: "5px 20px",
																			border: "none",
																			borderRadius: "5px",
																			cursor: "pointer",
																		}}>
																		Edit
																	</button>
																	<button
																		onClick={() => handleDelete(record)}
																		style={{
																			backgroundColor: "rgb(199, 81, 81)",
																			color: "white",
																			padding: "5px 20px",
																			border: "none",
																			borderRadius: "5px",
																			cursor: "pointer",
																		}}>
																		Delete
																	</button>
																</div>
															),
														},
													]}
													pagination={false}
												/> */}

												<div style={{ textAlign: "right", marginBottom: 16 }}>
													<Dropdown overlay={menu}>
														<Button>
															Sort By <DownOutlined />
														</Button>
													</Dropdown>
												</div>

												<Table
													scroll={{ x: 1200, y: 500 }}
													style={{ width: "100%" }}
													dataSource={result1}
													columns={[
														...columns,
														{
															title: "Actions",
															key: "actions",
															render: (_, record) => {
																const isApprove = approvedData.some((item) => item._id === record._id); // Check if the current row is approved

																return (
																	<div
																		style={{
																			display: "flex",
																			justifyContent: "space-between",
																			gap: "10px",
																		}}
																	>
																		<button
																			onClick={() => handleEdit(record)}
																			style={{
																				backgroundColor: "rgba(2, 130, 204, 0.74)",
																				color: "white",
																				padding: "5px 20px",
																				border: "none",
																				borderRadius: "5px",
																				cursor: "pointer",
																			}}
																		>
																			Edit
																		</button>
																		<button
																			onClick={() => handleDelete(record)}
																			style={{
																				backgroundColor: "rgb(199, 81, 81)",
																				color: "white",
																				padding: "5px 20px",
																				border: "none",
																				borderRadius: "5px",
																				cursor: "pointer",
																			}}
																		>
																			Delete
																		</button>
																		<button
																			onClick={() => handleApprove(record)} // Toggle approve
																			style={{
																				backgroundColor: isApprove ? "green" : "gray", // Change color based on approval status
																				color: "white",
																				padding: "5px 20px",
																				border: "none",
																				borderRadius: "5px",
																				cursor: "pointer",
																			}}
																		>
																			{isApprove ? "Approved" : "Approve"}
																		</button>
																	</div>
																);
															},
														},
													]}
													pagination={false}
												/>
											</Space>
											{/* <Form.Item> */}

											<div style={{
												width: '100%',
												// border:'2px solid',
												display: 'flex',
												justifyContent: 'space-between'
											}}>
												<button
													// onClick={() => hand}
													onClick={() => handleAdd()}
													style={{
														backgroundColor: "rgba(52, 170, 52, 0.74)",
														color: "white",
														padding: "5px 20px",
														border: "none",
														borderRadius: "5px",
														cursor: "pointer",
														marginLeft: '5px'

													}}>
													Add New User Story
												</button>
												<div >
													<Button
														type="primary"
														// style={{ width: '16%', marginTop: '20px' }}
														style={{ marginRight: '10px' }}
														// icon={<SearchOutlined />}
														onClick={() => downloadCSV(result1)}

													>
														Download Stories
													</Button>
													<Button
														type="primary"
														// style={{ marginTop: "25px" }}
														onClick={handleApproveStories}>
														Approve All Stories
													</Button>
												</div>
											</div>
											{/* </Form.Item> */}
										</div>
									)}


									{approvedStories.length > 0 &&
										<>
											<h1>Approved Stories</h1>

											<div
												style={{
													width: "100%",
													border: "1px solid #ccc",
													padding: 10,
													borderRadius: "10px",
													marginBottom: "10px",
													marginTop: "10px"
												}}>
												<Table
													scroll={{ x: 1200, y: 500 }}
													style={{ width: "100%" }}
													dataSource={approvedStories}
													// columns={columns}
													columns={[
														...columns,
														{
															title: "Actions",
															key: "actions",
															render: (_, record) => {
																const isApprove = approvedData.some((item) => item._id === record._id); // Check if the current row is approved

																return (
																	<div
																		style={{
																			display: "flex",
																			justifyContent: "space-between",
																			gap: "10px",
																		}}
																	>
																		<button
																			onClick={() => handleRemoveStory(record)} // Toggle approve
																			style={{
																				// backgroundColor: isApprove ? "green" : "gray", // Change color based on approval status
																				backgroundColor: "red",
																				color: "white",
																				padding: "5px 20px",
																				border: "none",
																				borderRadius: "5px",
																				cursor: "pointer",
																			}}
																		>
																			remove
																			{/* {isApprove ? "Remove" : "Approve"} */}
																		</button>
																	</div>
																);
															},
														},
													]}
													pagination={false}
												/>
											</div>
										</>
									}

									{/* {result1.length > 0 && showFeedBack && (
									<div
										style={{
											display: "flex",
											alignItems: "center",
											width: "81%",
											border: "1px solid #ccc",
											paddingRight: 15,
											paddingLeft: 15,
											marginBottom: 5,
											borderRadius: "10px",
										}}></div>
								)} */}

									{approvedStories.length > 0 && (
										<>
											<div
												style={{
													width: "100%",
													border: "1px solid #ccc",
													padding: 10,
													borderRadius: "10px",
												}}>
												<Form
													layout="vertical"
													style={{
														width: "100%",
														display: "flex",
														alignItems: "center",
														justifyContent: "end",
													}}>
													<div style={{
														display: "flex",
														justifyContent: "space-between",
														width: "29%",
														marginRight: "37px",
													}}>
														<Form.Item label="Agent 1">
															<Select
																value={agent1}
																onChange={(value) => handleAgentChange(value, setAgent1, [agent2, agent3])}
																options={agentOptions.map((option) => ({
																	...option,
																	disabled: selectedAgents.includes(option.value) && option.value !== agent1,
																}))}
															/>
														</Form.Item>

														<Form.Item label="Agent 2" >
															<Select
																value={agent2}
																// style={{margin: "0px 5px"}}
																onChange={(value) => handleAgentChange(value, setAgent2, [agent1, agent3])}
																options={agentOptions.map((option) => ({
																	...option,
																	disabled: selectedAgents.includes(option.value) && option.value !== agent2,
																}))}
															/>
														</Form.Item>

														<Form.Item label="Agent 3">
															<Select
																// style={{marginLeft: " 5px"}}


																value={agent3}
																onChange={(value) => handleAgentChange(value, setAgent3, [agent1, agent2])}
																options={agentOptions.map((option) => ({
																	...option,
																	disabled: selectedAgents.includes(option.value) && option.value !== agent3,
																}))}
															/>
														</Form.Item>
													</div>

													<Form.Item label="Prioritization Technique">
														<Select
															placeholder="Select Technique"
															optionFilterProp="children"
															onChange={handleLanguage}
															value={prioritizationTechnique}
															options={labelOptions}
															style={{ marginRight: " 10px" }}

														/>
													</Form.Item>
													<Form.Item label="Rounds">
														<Input
															type="number"
															value={rounds}
															onChange={(e) => setRounds(e.target.value)}
															style={{ margin: "0px 5px" }}
														/>
													</Form.Item>
													<Form.Item
														label="Model"
														style={{ marginLeft: "10px", marginRight: "10px" }}>
														<Select
															placeholder="Select Model"
															optionFilterProp="children"
															onChange={handleModel}
															value={selectModel}
															defaultValue="gpt-4o-mini"
															options={llmModels}
														/>
													</Form.Item>
													<Form.Item
														style={{
															display: "flex",
															alignItems: "end",
															marginTop: "25px",
														}}>
														<Button
															type="primary"
															icon={<SearchOutlined />}
															onClick={handleSubmit}


															disabled={prioritizationTechnique === null}>
															Generate
														</Button>
													</Form.Item>
												</Form>
											</div>
										</>
									)}


									{displayChatBox && (
										<div>
											{responses && (
												<div style={{ paddingTop: "10px" }}>
													{renderChatMessages()}
												</div>
											)}
										</div>
									)}
								</Panel>
							</Collapse>

						</div>
					</Content>
				</Layout>
				{/* <Footer className="footerFixed">
					<div style={{ float: "right", lineHeight: 0 }}>
						<p>&copy; {new Date().getFullYear()} GPT LAB. All rights reserved.</p>
					</div>
				</Footer> */}
			</Layout>
		</>
	);
};
export default App;
