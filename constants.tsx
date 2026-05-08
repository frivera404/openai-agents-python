
import React from 'react';
import type { Agent } from './types';

const DataScienceIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0h6m-6-10h6m0 0V5a2 2 0 00-2-2h-2a2 2 0 00-2 2v4" /></svg>;
const RAGIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 18v-6H5v6h4z" /></svg>;
const FinancialAdvisorIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>;
const MarketingAgencyIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-2.036 9.168-5" /></svg>;
const CustomerServiceIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a2 2 0 01-2-2V7a2 2 0 012-2h2.586a1 1 0 01.707.293l2.414 2.414a1 1 0 01.293.707V8z" /></svg>;
const AcademicResearchIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v11.494m-9-5.494h18" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.5 9.755l7.5 4.286 7.5-4.286M12 21.75V16.5" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.5 14.25v-4.5" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 14.25v-4.5" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2.25l7.5 4.286M4.5 6.536l7.5 4.286" /></svg>;
const BugAssistantIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 8.25l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>;
const TravelConciergeIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9V3" /></svg>;
const TimeSeriesIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12h1m16 0h1m-8-5v1m0 8v1" /></svg>;
const LLMAuditorIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4" /></svg>;
const ShoppingIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" /></svg>;
const SearchOptimizationIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-lime-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>;
const FOMCIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12l-9-9-9 9m18 0H3m18 0l-9 9-9-9" /></svg>;


export const AGENTS: Agent[] = [
    {
        id: 'customer-service',
        name: 'Customer Service Agent',
        description: 'Delivers support by analyzing issues, provides recommendations, discounts, helps customers check out, and facilitates transactions using handoffs between specialized agents.',
        language: 'Python',
        icon: <CustomerServiceIcon />,
    },
    {
        id: 'financial-research',
        name: 'Financial Research Agent',
        description: 'Composes financial research reports by planning search terms, retrieving data, analyzing fundamentals and risks, writing reports, and verifying accuracy.',
        language: 'Python',
        icon: <FinancialAdvisorIcon />,
    },
    {
        id: 'research-bot',
        name: 'Research Bot',
        description: 'Conducts comprehensive research by planning queries, searching the web, analyzing results, and generating structured reports with citations.',
        language: 'Python',
        icon: <AcademicResearchIcon />,
    },
    {
        id: 'senior-developer',
        name: 'Senior Developer Agent',
        description: 'Acts as a senior developer using OpenAI Assistants API with vector store for knowledge retrieval, providing code-related advice and using MCP tools for filesystem operations.',
        language: 'Python',
        icon: <BugAssistantIcon />,
    },
    {
        id: 'data-science',
        name: 'Data Science',
        description: 'Queries diverse data across multiple sources using natural language, builds predictive models, visualizes trends, and communicates key insights.',
        language: 'Python',
        icon: <DataScienceIcon />,
    },
    {
        id: 'rag',
        name: 'Retrieval-Augmented Generation (RAG)',
        description: 'Uses RAG to get information from specified knowledge sources, ensuring responses are factually grounded, context-aware, and up-to-date.',
        language: 'Python',
        icon: <RAGIcon />,
    },
    {
        id: 'marketing-agency',
        name: 'Marketing Agency',
        description: 'Streamlines new website and product launches. Identifies optimal DNS domains, generates entire websites, and develops marketing strategies.',
        language: 'Python',
        icon: <MarketingAgencyIcon />,
    },
    {
        id: 'travel-concierge',
        name: 'Travel Concierge',
        description: 'Orchestrates personalized travel experiences and provides support throughout the user’s journey, from planning to real-time itinerary alerts.',
        language: 'Python',
        icon: <TravelConciergeIcon />,
    },
    {
        id: 'time-series',
        name: 'Time Series Forecasting',
        description: 'Automates time-series forecasting by leveraging BigQuery ML. Provides clear, explained predictions to support data-driven business decisions.',
        language: 'Java',
        icon: <TimeSeriesIcon />,
    },
    {
        id: 'llm-auditor',
        name: 'LLM Auditor',
        description: 'Evaluates LLM-generated answers, verifies actual accuracy using the web, and refines the response to ensure alignment with real-world knowledge.',
        language: 'Python',
        icon: <LLMAuditorIcon />,
    },
    {
        id: 'shopping',
        name: 'Personalized Shopping',
        description: 'Delivers personalized recommendations, tailored to specific brands, merchants, or marketplaces.',
        language: 'Python',
        icon: <ShoppingIcon />,
    },
    {
        id: 'brand-search',
        name: 'Brand Search Optimization',
        description: 'Analyzes top brand-related keywords and competitor search results, and generates suggestions to enhance a brand’s search engine ranking.',
        language: 'Python',
        icon: <SearchOptimizationIcon />,
    },
    {
        id: 'fomc-research',
        name: 'FOMC Research',
        description: 'Extracts web data, analyzes complex topics, executes custom functions, and generates summary reports from multi-modal data comparisons.',
        language: 'Python',
        icon: <FOMCIcon />,
    },
];
