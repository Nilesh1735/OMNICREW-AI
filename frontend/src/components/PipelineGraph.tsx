import React, { useMemo } from 'react';
import ReactFlow, { Background, Controls, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';
import { AgentLog } from '../types';

interface PipelineGraphProps {
  logs: AgentLog[];
  isProcessing: boolean;
}

const PipelineGraph: React.FC<PipelineGraphProps> = ({ logs, isProcessing }) => {
  const lastLog = logs.length > 0 ? logs[logs.length - 1] : null;
  
  const isResearcherActive = isProcessing && lastLog?.agent_name === 'System' && lastLog?.action.includes('Executing');
  const isAnalystActive = isProcessing && lastLog?.agent_name === 'Manager' && lastLog?.action.includes('Validation');
  
  // Hardcoded LLM tracking logic for OpenAI -> Mistral -> Gemini
  const isOpenAIActive = logs.some(l => l.thought_process?.toLowerCase().includes('openai') && l.action === 'LLM Routing');
  const isOpenAIFailed = logs.some(l => l.action === 'LLM Fallback') && logs.some(l => l.thought_process?.toLowerCase().includes('openai'));
  
  const isMistralActive = logs.some(l => l.thought_process?.toLowerCase().includes('mistral') && l.action === 'LLM Routing');
  const isMistralFailed = logs.some(l => l.action === 'LLM Fallback') && logs.some(l => l.thought_process?.toLowerCase().includes('mistral'));
  
  const isGeminiActive = logs.some(l => l.thought_process?.toLowerCase().includes('gemini') && l.action === 'LLM Routing');

  const nodes: Node[] = useMemo(() => [
    { id: '1', data: { label: 'Autonomous_Prompt' }, position: { x: 0, y: 100 }, className: 'custom-node' },
    { id: '2', data: { label: 'Web_Researcher' }, position: { x: 250, y: 100 }, className: `custom-node ${isResearcherActive ? 'node-breathing' : ''}` },
    { id: '3', data: { label: 'Extraction_Analyst' }, position: { x: 500, y: 100 }, className: `custom-node ${isAnalystActive ? 'node-breathing' : ''}` },
    { id: '4', data: { label: 'Dynamic_DB' }, position: { x: 750, y: 100 }, className: 'custom-node' },
    { id: '5', data: { label: 'OpenAI' }, position: { x: 350, y: -50 }, className: `custom-node llm-node ${isOpenAIActive ? 'node-breathing' : ''} ${isOpenAIFailed ? 'node-failed' : ''}` },
    { id: '6', data: { label: 'Mistral AI' }, position: { x: 500, y: -50 }, className: `custom-node llm-node ${isMistralActive ? 'node-breathing' : ''} ${isMistralFailed ? 'node-failed' : ''}` },
    { id: '7', data: { label: 'Gemini' }, position: { x: 650, y: -50 }, className: `custom-node llm-node ${isGeminiActive ? 'node-breathing' : ''}` },
  ], [isResearcherActive, isAnalystActive, isOpenAIActive, isOpenAIFailed, isMistralActive, isMistralFailed, isGeminiActive]);

  const edges: Edge[] = useMemo(() => [
    { id: 'e1-2', source: '1', target: '2', animated: isProcessing, className: 'custom-edge' },
    { id: 'e2-3', source: '2', target: '3', animated: isResearcherActive, className: 'custom-edge' },
    { id: 'e3-4', source: '3', target: '4', animated: isAnalystActive, className: 'custom-edge' },
    { id: 'e2-5', source: '2', target: '5', animated: isOpenAIActive, className: 'custom-edge' },
    { id: 'e5-6', source: '5', target: '6', animated: isOpenAIFailed, className: 'custom-edge' },
    { id: 'e6-7', source: '6', target: '7', animated: isMistralFailed, className: 'custom-edge' },
    { id: 'e5-3', source: '5', target: '3', animated: isOpenAIActive, className: 'custom-edge' },
    { id: 'e6-3', source: '6', target: '3', animated: isMistralActive, className: 'custom-edge' },
    { id: 'e7-3', source: '7', target: '3', animated: isGeminiActive, className: 'custom-edge' },
  ], [isProcessing, isResearcherActive, isAnalystActive, isOpenAIActive, isOpenAIFailed, isMistralActive, isMistralFailed, isGeminiActive]);

  return (
    <div style={{ height: '300px', width: '100%' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView className="bg-transparent">
        <Background color="#2a2a3a" gap={16} size={1} />
        <Controls className="custom-controls" showInteractive={false} showZoom={false} showFitView={false} />
      </ReactFlow>
    </div>
  );
};

export default PipelineGraph;