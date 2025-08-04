

import { Form, Input, Button, Breadcrumb } from 'antd';
import React, { useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation, useParams } from 'react-router-dom';

const Add_Personas = () => {
    const inputRef = useRef(null);
    const [form] = Form.useForm();
    const navigate = useNavigate();
    const location = useLocation();
    const personaToEdit = location.state?.persona || null;
    const { id } = useParams();

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    useEffect(() => {
        if (personaToEdit) {
            form.setFieldsValue(personaToEdit);
        }
        inputRef.current?.focus();
    }, [personaToEdit, form]);

    const handleAddPersona = async (values) => {
        const newPersona = {
            name: values.name,
            role: values.role,
            default_icon: values.default_icon || "🆕",
            tasks: values.tasks.map((task) => ({
                taskName: task.taskName,
                taskLabel: task.taskLabel || task.taskName,
                prompt: task.prompt,
            })),
            project_id: id
        };

        try {
            let response;
            if (personaToEdit) {
                response = await fetch(`/api/update-persona/${personaToEdit._id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(newPersona),
                });
            } else {
                response = await fetch("/api/add-personas", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(newPersona),
                });
            }

            if (response.ok) {
                form.resetFields();
                navigate(`/agent_list/${id}`);
            }
        } catch (error) {
            console.error("Error saving persona:", error);
        }
    };

    return (
        <>
            <Breadcrumb
                separator=""
                items={[
                    { title: <Link to="/">Home</Link> },
                    { type: 'separator' },
                    { title: <Link to={`/agent_list/${id}`}>Agents List</Link> },
                    { type: 'separator' },
                    { title: <Link to={`/add_agent/${id}`}>Add Agent</Link> },
                ]}
            />
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <h2>{personaToEdit ? "Edit Agent Profile" : "Add New Agent Profile"}</h2>
                <Form
                    form={form}
                    onFinish={handleAddPersona}
                    layout="vertical"
                    style={{ width: "50%", border: "1px solid gray", borderRadius: "10px", padding: "10px", boxShadow: "-1px 9px 10px rgba(0, 0, 0, 0.2)" }}
                >
                    <Form.Item name="name" label="Persona Name" rules={[{ required: true, message: "Enter persona name" }]}>
                        <Input ref={inputRef} placeholder="Enter persona name" />
                    </Form.Item>

                    <Form.Item name="role" label="Role" rules={[{ required: true, message: "Enter persona role" }]}>
                        <Input placeholder="Enter role (e.g., Dev, QA)" />
                    </Form.Item>

                    <Form.Item name="default_icon" label="Icon Name">
                        <Input placeholder="Enter an emoji name " />
                    </Form.Item>

                    <Form.List
                        name="tasks"
                        initialValue={[
                            { taskName: "user_story_generation", taskLabel: "User Story Generation", prompt: "" },
                            { taskName: "prioritization", taskLabel: "Prioritization", prompt: "" },
                        ]}
                    >
                        {(fields, { add, remove }) => (
                            <div>
                                {fields.map(({ key, name, ...restField }, index) => (
                                    <div key={key} style={{ marginBottom: "10px", border: "1px solid #ccc", padding: "10px", borderRadius: "5px" }}>
                                        <h3>{index < 2 ? `Task Name (${index === 0 ? "User Story Generation" : "Prioritization"})` : "New Task"}</h3>

                                        {index >= 2 && (
                                            <Form.Item {...restField} name={[name, "taskName"]} label="Task Name" rules={[{ required: true, message: "Enter task name" }]}> 
                                                <Input placeholder="Enter task name" />
                                            </Form.Item>
                                        )}

                                        <Form.Item {...restField} name={[name, "prompt"]} label="Task Prompt" rules={[{ required: true, message: "Enter task prompt" }]}> 
                                            <Input.TextArea placeholder="Enter task prompt description" />
                                        </Form.Item>

                                        {index > 1 && (
                                            <Button danger onClick={() => remove(name)}>
                                                Remove Task
                                            </Button>
                                        )}
                                    </div>
                                ))}
                                <Button type="dashed" onClick={() => add()} block>
                                    Add Task
                                </Button>
                            </div>
                        )}
                    </Form.List>

                    <div style={{ textAlign: "center" }}>
                        <Button type="primary" htmlType="submit" style={{ margin: '20px', width: "90%" }}>
                            {personaToEdit ? "Update Agent" : "Add Persona"}
                        </Button>
                    </div>
                </Form>
            </div>
        </>
    );
};

export default Add_Personas;
