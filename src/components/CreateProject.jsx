
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchProjects,
  fetchUserStories,
  createProject,
  deleteProject,
  // deleteUserStory,
  setUserStorySelected,
  deleteUserStoryVersion
} from "../features/MainSlice.jsx";
import {
  Button,
  Input,
  message,
  Form,
  List,
  Card,
  Spin,
  Row,
  Col,
  Typography,
  Badge,
  Divider,
  Tag,
  Empty,
  Space
} from "antd";
import { useLocation, useNavigate } from "react-router-dom";
import {
  DeleteOutlined,
  FolderOpenOutlined,
  PlusOutlined,
  ProjectOutlined,
  HistoryOutlined,
  FileSearchOutlined,
  ClockCircleOutlined
} from "@ant-design/icons";

const { Title, Text } = Typography;

const CreateProject = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const location = useLocation();
  const [form] = Form.useForm();

  // Get state from Redux
  const { projects, userStories, loading } = useSelector((state) => state.main);

  
  
  useEffect(() => {
    dispatch(fetchProjects());
    dispatch(fetchUserStories());
  }, []);

  console.log(userStories);

  useEffect(() => {
    // Check if reload has already happened for this visit
    const hasReloaded = sessionStorage.getItem(`hasReloaded_${location.pathname}`);

    if (!hasReloaded) {
      sessionStorage.setItem(`hasReloaded_${location.pathname}`, "true");
      window.location.reload(); // Force reload on first entry
    }

    // Reset the reload flag when user leaves the page
    return () => {
      sessionStorage.removeItem(`hasReloaded_${location.pathname}`);
    };
  }, [location.pathname]);

  const handleDeleteProject = (projectId) => {
    dispatch(deleteProject(projectId))
      .unwrap()
      .then(() => {
        message.success("Project deleted successfully!");
      })
      .catch((error) => {
        message.error("Failed to delete project: " + error);
      });
  };

  const handleDeleteUserStoryVersion = (storyId) => {
    dispatch(deleteUserStoryVersion(storyId))
      .unwrap()
      .then(() => {
        message.success("User story deleted successfully!");
        dispatch(fetchUserStories());

      })
      .catch((error) => {
        message.error("Failed to delete user story: " + error);
      });
  };

  const handleCreateProject = (values) => {
    dispatch(createProject(values.projectName))
      .unwrap()
      .then(() => {
        message.success("Project Created!");
        form.resetFields();
        // console.log(form);
        dispatch(fetchProjects());
        
      })
      .catch((error) => {
        message.error("Failed to create project: " + error);
      });
  };

  // Group user stories by project and add version numbers
  // const getProjectUserStories = (projectId) => {
  //   const filteredStories = userStories.filter(
  //     (story) => story.project_id === projectId
  //   );

  //   return filteredStories.map((story, index) => ({
      
  //     ...story,
  //     versionNumber: `Version ${index + 1}`,
  //     date: story.date ? new Date(story.date).toLocaleDateString() : new Date().toLocaleDateString(),
  //   }));
  // };

  const getProjectUserStories = (projectId) => {
    const filteredStories = userStories.filter(
      (story) => story.project_id === projectId
    );
  
    return filteredStories.map((story, index) => {
      const storyDate = new Date(story.created_at); // Use the stored DB date
  
      return {
        ...story,
        versionNumber: `Version ${index + 1}`,
        formattedDate: storyDate.toLocaleDateString("en-US"), // e.g., 03/19/2025
        formattedTime: storyDate.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" }), // e.g., 09:15:41 AM
      };
    });
  };
  
  


  const handleOpenProjectVersion = (project, story) => {
    dispatch(setUserStorySelected(story._id)); // Set story ID in Redux store
    navigate(`/project/${project.id}`); // Navigate after state update
  };

  const handleOpenProject = (project) => {
    dispatch(setUserStorySelected(null)); // Set story ID in Redux store
    navigate(`/project/${project.id}`); // Navigate after state update
  };

  return (
    <div style={{ padding: "24px", backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
      <Title level={2} style={{ marginBottom: "24px", color: "#1890ff" }}>
        <ProjectOutlined /> Project Management
      </Title>

      <Row gutter={24}>
        {/* Create Project Section (Left Side) */}
        <Col xs={24} md={8}>
          <Card variant="outlined"
            title={
              <Space>
                <PlusOutlined />
                <span>Create New Project</span>
              </Space>
            }
            bordered={false}
            style={{
              height: "100%",
              boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
              borderRadius: "8px"
            }}
          >
            <Form form={form} onFinish={handleCreateProject} layout="vertical">
              <Form.Item
                label="Project Name"
                name="projectName"
                rules={[{ required: true, message: "Project name cannot be empty" }]}
              >
                <Input
                  placeholder="Enter project name"
                  size="large"
                  prefix={<ProjectOutlined style={{ color: "#1890ff" }} />}
                />
              </Form.Item>
              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  style={{ width: "100%" }}
                  icon={<PlusOutlined />}
                  loading={loading}
                >
                  Create Project
                </Button>
              </Form.Item>
            </Form>

            <Divider />

            <div style={{ textAlign: "center" }}>
              {/* <img 
                src="/api/placeholder/280/180" 
                alt="Project Management" 
                style={{ opacity: 0.7, maxWidth: "100%" }}
              /> */}
              <Text type="secondary" style={{ display: "block", marginTop: "12px" }}>
                Create a new project and start adding user stories
              </Text>
            </div>
          </Card>
        </Col>

        {/* Projects List (Right Side) */}
        <Col xs={24} md={16}>
          <Card variant="outlined"
            title={
              <Space>
                <FolderOpenOutlined />
                <span>Your Projects</span>
                <Badge count={projects.length} style={{ backgroundColor: "#52c41a" }} />
              </Space>
            }
            bordered={false}
            style={{ boxShadow: "0 1px 2px rgba(0,0,0,0.1)", borderRadius: "8px" }}
          >
            {loading ? (
              <div style={{ textAlign: "center", padding: "20px" }}>
                <Spin size="large" />
              </div>
            ) : projects.length > 0 ? (
              <List
                dataSource={projects}
                itemLayout="vertical"
                renderItem={(project) => {
                  const projectStories = getProjectUserStories(project.id);
                  return (
                    <Card variant="outlined"
                      className="project-card"
                      title={
                        <Space>
                          <ProjectOutlined style={{ color: "#1890ff" }} />
                          <Text strong>{project.project_name}</Text>
                        </Space>
                      }
                      extra={
                        <Space>
                          <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => handleDeleteProject(project.id)}
                          />
                          <Button
                            type="primary"
                            icon={<FolderOpenOutlined />}
                            // onClick={() => navigate(`/project/${project.id}`)}
                            onClick={()=>handleOpenProject(project)}
                          >
                            create new stories
                          </Button>
                        </Space>
                      }
                      style={{
                        marginBottom: "16px",
                        borderLeft: "3px solid #1890ff"
                      }}
                    >
                      <Space
                        direction="vertical"
                        style={{ width: "100%" }}
                        size="middle"
                      >
                        <div>
                          <Text type="secondary">
                            <HistoryOutlined /> Version History ({projectStories.length})
                          </Text>
                          <Divider style={{ margin: "8px 0" }} />
                        </div>

                        {projectStories.length > 0 ? (
                          <List
                            size="small"
                            dataSource={projectStories}
                            renderItem={(story, index) => (
                              <List.Item
                                key={story.id}
                                actions={[
                                  <Button
                                    type="text"
                                    danger
                                    icon={<DeleteOutlined />}
                                    size="small"
                                    onClick={() => handleDeleteUserStoryVersion(story._id)}
                                  />,
                                  <Button
                                    type="primary"
                                    icon={<FileSearchOutlined />}
                                    size="small"
                                    onClick={()=>handleOpenProjectVersion(project, story)} // Updated to use story.id
                                  >
                                    Open
                                  </Button>
                                ]}
                                style={{
                                  padding: "8px 16px",
                                  borderRadius: "4px",
                                  backgroundColor: index % 2 === 0 ? "#f9f9f9" : "transparent",
                                  borderLeft: "2px solid #52c41a",
                                  marginBottom: "8px",
                                  display:'flex',
                                  justifyContent:'center',
                                  alignItems:'center'
                                }}
                              >
                                <Space>
                                  <Tag color="green">{story.versionNumber}</Tag>
                                  <Text>{story.story_name}</Text>
                                </Space>
                                {/* <Text type="secondary" style={{ fontSize: "12px" }}>
                      <ClockCircleOutlined style={{ marginRight: 4 }} />
                      {story.date}
                    </Text>
                     */}
                     <Text type="secondary" style={{ fontSize: "12px" }}>
                      <ClockCircleOutlined style={{ marginRight: 4 }} />
                      {story.formattedDate} - {story.formattedTime}
                    </Text>

                    <Text type="secondary" style={{ fontSize: "12px", marginLeft:'5px' }}>
                       {/* {story.response_time}    */}
                      duration {Math.floor(story.response_time)} seconds
                    </Text>
                              </List.Item>
                            )}
                          />
                        ) : (
                          <Empty
                            description="No user stories yet"
                            image={Empty.PRESENTED_IMAGE_SIMPLE}
                          />
                        )}
                      </Space>
                    </Card>
                  );
                }}
              />
            ) : (
              <Empty description="No projects found. Create your first project!" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CreateProject;