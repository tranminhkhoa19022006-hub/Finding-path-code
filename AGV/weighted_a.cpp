#include "nav2_weighted_astar_planner/weighted_astar_planner.hpp"
#include "pluginlib/class_list_macros.hpp"
#include <cmath>
#include <algorithm>
#include <queue>
#include <unordered_map>

namespace nav2_weighted_astar_planner
{

void WeightedAStarPlanner::configure(
  const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
  std::string name,
  std::shared_ptr<tf2_ros::Buffer> tf,
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros)
{
  node_ = parent.lock();
  name_ = name;
  tf_ = tf;
  costmap_ = costmap_ros->getCostmap();
  global_frame_ = costmap_ros->getGlobalFrameID();

  origin_x_ = costmap_->getOriginX();
  origin_y_ = costmap_->getOriginY();
  width_ = costmap_->getSizeInCellsX();
  height_ = costmap_->getSizeInCellsY();
  resolution_ = costmap_->getResolution();
  map_size_ = width_ * height_;

  RCLCPP_INFO(node_->get_logger(), "Weighted A* Planner initialized");
}

void WeightedAStarPlanner::cleanup() { }
void WeightedAStarPlanner::activate() { }
void WeightedAStarPlanner::deactivate() { }

nav_msgs::msg::Path WeightedAStarPlanner::createPlan(
  const geometry_msgs::msg::PoseStamped & start,
  const geometry_msgs::msg::PoseStamped & goal)
{
  nav_msgs::msg::Path global_path;
  global_path.header.stamp = node_->now();
  global_path.header.frame_id = global_frame_;

  // Flatten costmap
  std::vector<int> costmap_flat(map_size_);
  for (size_t idx = 0; idx < map_size_; ++idx) {
    int x = idx % width_;
    int y = std::floor(idx / width_);
    costmap_flat.at(idx) = static_cast<int>(costmap_->getCost(x, y));
  }

  float start_x = start.pose.position.x;
  float start_y = start.pose.position.y;
  float goal_x = goal.pose.position.x;
  float goal_y = goal.pose.position.y;

  size_t start_index = 0, goal_index = 0;
  if (inGridMapBounds(start_x, start_y) && inGridMapBounds(goal_x, goal_y)) {
    fromWorldToGrid(start_x, start_y);
    fromWorldToGrid(goal_x, goal_y);
    start_index = gridCellxyToIndex(start_x, start_y);
    goal_index = gridCellxyToIndex(goal_x, goal_y);
  } else {
    RCLCPP_WARN(node_->get_logger(), "Start or goal outside map bounds");
    return global_path;
  }

  std::vector<int> shortest_path;
  if (!weightedAStarShortestPath(start_index, goal_index, costmap_flat, shortest_path)) {
    RCLCPP_WARN(node_->get_logger(), "Weighted A*: No path found");
    return global_path;
  }

  for (int p : shortest_path) {
    int x, y;
    fromIndexToGridCellxy(p, x, y);
    float wx = static_cast<float>(x);
    float wy = static_cast<float>(y);
    fromGridToWorld(wx, wy);

    geometry_msgs::msg::PoseStamped pose;
    pose.pose.position.x = wx;
    pose.pose.position.y = wy;
    pose.pose.orientation.w = 1.0;
    pose.header.stamp = node_->now();
    pose.header.frame_id = global_frame_;
    global_path.poses.push_back(pose);
  }

  global_path.poses.push_back(goal);
  return global_path;
}

bool WeightedAStarPlanner::weightedAStarShortestPath(
  const int & start_index, const int & goal_index,
  const std::vector<int> & costmap_flat, std::vector<int> & shortest_path)
{
  struct Node {
    int index;
    double g, f;
    bool operator>(const Node & other) const { return f > other.f; }
  };

  auto heuristic = [&](int idx) {
    int x = idx % width_;
    int y = idx / width_;
    int gx = goal_index % width_;
    int gy = goal_index / width_;
    return std::abs(x - gx) + std::abs(y - gy); // Manhattan
  };

  std::priority_queue<Node, std::vector<Node>, std::greater<Node>> open;
  std::unordered_map<int, double> g_score;
  std::unordered_map<int, int> came_from;

  g_score[start_index] = 0.0;
  double h_start = heuristic(start_index);
  open.push({start_index, 0.0, 0.0 + (1 + h_start / (0.0 + 1e-5)) * h_start});

  while (!open.empty()) {
    Node current = open.top();
    open.pop();

    if (current.index == goal_index) {
      int idx = goal_index;
      while (came_from.find(idx) != came_from.end()) {
        shortest_path.push_back(idx);
        idx = came_from[idx];
      }
      shortest_path.push_back(start_index);
      std::reverse(shortest_path.begin(), shortest_path.end());
      return true;
    }

    // neighbors: 4 directions
    std::vector<int> neighbors;
    int x = current.index % width_;
    int y = current.index / width_;
    if (x > 0) neighbors.push_back(current.index - 1);
    if (x < (int)width_ - 1) neighbors.push_back(current.index + 1);
    if (y > 0) neighbors.push_back(current.index - width_);
    if (y < (int)height_ - 1) neighbors.push_back(current.index + width_);

    for (int nb : neighbors) {
      if (costmap_flat[nb] >= 254) continue; // obstacle
      double step_cost = 1.0;
      double tentative_g = g_score[current.index] + step_cost;
      if (!g_score.count(nb) || tentative_g < g_score[nb]) {
        came_from[nb] = current.index;
        g_score[nb] = tentative_g;
        double h = heuristic(nb);
        double f = tentative_g + (1 + h / (tentative_g + 1e-5)) * h;
        open.push({nb, tentative_g, f});
      }
    }
  }
  return false;
}

void WeightedAStarPlanner::fromWorldToGrid(float & x, float & y) {
  x = static_cast<size_t>((x - origin_x_) / resolution_);
  y = static_cast<size_t>((y - origin_y_) / resolution_);
}

bool WeightedAStarPlanner::inGridMapBounds(const float & x, const float & y) {
  return !(x < origin_x_ || y < origin_y_ ||
           x > origin_x_ + (width_ * resolution_) ||
           y > origin_y_ + (height_ * resolution_));
}

size_t WeightedAStarPlanner::gridCellxyToIndex(const float & x, const float & y) {
  return y * width_ + x;
}

void WeightedAStarPlanner::fromIndexToGridCellxy(size_t index, int & x, int & y) {
  x = index % width_;
  y = std::floor(index / width_);
}

void WeightedAStarPlanner::fromGridToWorld(float & x, float & y) {
  x = x * resolution_ + origin_x_;
  y = y * resolution_ + origin_y_;
}

}  // namespace nav2_weighted_astar_planner

PLUGINLIB_EXPORT_CLASS(nav2_weighted_astar_planner::WeightedAStarPlanner,
                       nav2_core::GlobalPlanner)
