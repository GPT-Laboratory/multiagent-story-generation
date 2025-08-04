

import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { updateItem, upgradeItem } from "./features/TableStoriesResponse.jsx";
import {
  Form,
  Input,
  Button,
  Typography,
  Card,
  Space,
  Breadcrumb,
  Select
} from 'antd';
import {
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  RocketOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { Vault } from "lucide-react";

const { Title } = Typography;
const { TextArea } = Input;

const EditItem = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const { key, id } = useParams();
  const [form] = Form.useForm();
  const [personasWithTasks, setPersonasWithTasks] = useState([])
  const agentOptions = personasWithTasks.map((persona) => ({
    value: persona.role,
    // label: persona.name,
  }));
  const [agent1, setAgent1] = useState("Product Owner");
  const result1 = useSelector((state) => state.tablestoriesresponse.result1);
  const story = result1.find((story) => story._id === id);
  console.log(key);


  const [formData, setFormData] = useState(() => ({ ...story }));
  const [prompt, setPrompt] = useState("");

  useEffect(() => {
    const fetchPersonas = async () => {
      try {
        const response = await fetch(`/api/personas/${key}`); // Send project_id
        const data = await response.json();
        setPersonasWithTasks(data);
      } catch (error) {
        console.error("Error fetching personas:", error);
      }
    };

    fetchPersonas();
    // fetchUserStories();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await dispatch(updateItem(formData)).unwrap();
      navigate(`/project/${key}`);
    } catch (error) {
      console.error("Update failed:", error);
    }
  };

  const handleUpgrade = async () => {
    try {
      const response = await dispatch(upgradeItem({ ...formData, agent1, prompt })).unwrap();
      console.log("Upgrade Response:", response);

      const upgradedStory = Array.isArray(response.upgraded_story) && response.upgraded_story.length > 0
        ? response.upgraded_story[0]
        : {};

      setFormData((prev) => ({
        ...prev,
        user_story: upgradedStory.user_story || prev.user_story,
        description: upgradedStory.description || prev.description,
        epic: upgradedStory.epic || prev.epic,
        suggestion: upgradedStory.suggestion || prev.suggestion,
      }));
    } catch (error) {
      console.error("Upgrade failed:", error);
    }
  };

  const handleAgentChange = (value) => {
    setAgent1(value)
  };

  return (
    <>
      <Breadcrumb style={{
        margin: '20px',
        marginLeft: '40px'
      }}>
        <Breadcrumb.Item><Link to="/">Projects List</Link></Breadcrumb.Item>
        <Breadcrumb.Item><Link to={`/project/${key}`} >Home Page</Link></Breadcrumb.Item>
        <Breadcrumb.Item><Link  >Edit Story</Link></Breadcrumb.Item>

        {/* <Breadcrumb.Item><Link to="/agent_list">Agents List</Link></Breadcrumb.Item> */}
      </Breadcrumb>
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 'calc(100vh - 64px)',
        padding: '24px'
      }}>
        <Card variant="outlined"
          style={{
            width: '100%',
            maxWidth: '600px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          }}
          title={
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <ArrowLeftOutlined
                style={{ fontSize: '20px', cursor: 'pointer', marginRight: '12px' }}
                onClick={() => navigate(`/project/${key}`)}
              />
              <Title level={3} style={{ textAlign: 'center', flex: 1, margin: 0 }}>
                <EditOutlined style={{ marginRight: 8 }} />
                Edit Item
              </Title>
            </div>
          }
        >
          <form onSubmit={handleUpdate}>
            {Object.keys(formData).map(
              (key) =>
                key !== "key" && key !== "_id" && (
                  <Form.Item
                    layout="vertical"
                    key={key}
                    label={<strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</strong>}

                    // label={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  >
                    {key === "user_story" || key === "description" ? (
                      <TextArea
                        name={key}
                        value={formData[key] || ""}
                        onChange={handleChange}
                        rows="4"
                      />
                    ) : (
                      <Input
                        name={key}
                        value={formData[key] || ""}
                        onChange={handleChange}
                      />
                    )}
                  </Form.Item>
                  

                )
            )}

            <Form.Item layout="vertical" label={<strong>Write Changes for User Story</strong>} >
              <div style={{display:'flex', alignItems:'center', width:'50%', justifyContent:'space-between'}}>
              <p style={{width:'30%', fontStyle:'bold'}}>Select Agent</p>
              <Select

                style={{ width:'70%' , marginBottom: '5px' }}
                value={agent1}
                onChange={(value) => handleAgentChange(value)}
                options={agentOptions.map((option) => ({
                  ...option,
                  // disabled: selectedAgents.includes(option.value) && option.value !== agent1,
                }))}
              />
              </div>

              <TextArea
                name="prompt"
                value={prompt}
                onChange={handlePromptChange}
                rows="4"
                placeholder="Enter what changes you want..."
              />

            </Form.Item>

            <Space direction="vertical" style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={<RocketOutlined />}
                block
                onClick={handleUpgrade}
              >
                Update with AI
              </Button>

              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Button
                  // type="primary"
                  variant="solid"
                  color="cyan"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  style={{ flex: 1, marginRight: 8 }}
                >
                  Approve
                </Button>
                <Button
                  type="default"
                  icon={<CloseOutlined />}
                  style={{ flex: 1 }}
                  onClick={() => navigate(`/project/${key}`)}
                >
                  Cancel
                </Button>
              </Space>
            </Space>
          </form>
        </Card>
      </div>
    </>
  );
};

export default EditItem;