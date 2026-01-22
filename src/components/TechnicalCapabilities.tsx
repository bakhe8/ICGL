import React from 'react';

interface Capability {
  title: string;
  description: string;
  details: string[];
}

const capabilities: Capability[] = [
  {
    title: 'Cloud Computing',
    description: 'Leveraging cloud platforms for scalable solutions.',
    details: [
      'Experience with AWS, Azure, and Google Cloud.',
      'Deployment of scalable microservices.',
      'Cloud-native application development.',
    ],
  },
  {
    title: 'Data Analysis',
    description: 'Analyzing and interpreting complex data sets.',
    details: [
      'Proficient in Python and R for data analysis.',
      'Experience with big data technologies like Hadoop and Spark.',
      'Data visualization using tools like Tableau and Power BI.',
    ],
  },
  {
    title: 'Machine Learning',
    description: 'Building predictive models and AI solutions.',
    details: [
      'Development of machine learning models using TensorFlow and PyTorch.',
      'Experience with natural language processing and computer vision.',
      'Deployment of AI models in production environments.',
    ],
  },
];

const TechnicalCapabilities: React.FC = () => {
  return (
    <div>
      <h1>Technical Capabilities</h1>
      {capabilities.map((capability, index) => (
        <div key={index}>
          <h2>{capability.title}</h2>
          <p>{capability.description}</p>
          <ul>
            {capability.details.map((detail, idx) => (
              <li key={idx}>{detail}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default TechnicalCapabilities;