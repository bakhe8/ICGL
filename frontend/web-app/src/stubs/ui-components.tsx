import React from 'react';

export const Button: React.FC<any> = (props) => {
    const { children, ...rest } = props;
    return React.createElement('button', rest, children ?? null);
};

export const Icon: React.FC<any> = () => null;

export const Card: React.FC<any> = (props) => React.createElement('div', props, props.children ?? null);

export const Mermaid: React.FC<any> = () => null;
export const SovereignTerminal: React.FC<any> = () => null;

const _default = { Button, Icon, Card };
export default _default;
