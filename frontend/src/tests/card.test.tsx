import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Card } from '@/components/common/Card';

describe('Card Component', () => {
  it('should render card with children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('should render with title', () => {
    render(<Card title="Card Title">Content</Card>);
    expect(screen.getByText('Card Title')).toBeInTheDocument();
  });

  it('should render with subtitle', () => {
    render(<Card subtitle="Card Subtitle">Content</Card>);
    expect(screen.getByText('Card Subtitle')).toBeInTheDocument();
  });

  it('should render with footer', () => {
    render(<Card footer={<div>Footer content</div>}>Content</Card>);
    expect(screen.getByText('Footer content')).toBeInTheDocument();
  });

  it('should render with title and subtitle', () => {
    render(
      <Card title="Title" subtitle="Subtitle">
        Content
      </Card>
    );
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Subtitle')).toBeInTheDocument();
  });

  it('should accept custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    const card = container.querySelector('.bg-white');
    expect(card).toHaveClass('custom-class');
  });
});