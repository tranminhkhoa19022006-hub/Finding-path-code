#ifndef NAV2_WEIGHTED_ASTAR_PLANNER_HPP_
#define NAV2_WEIGHTED_ASTAR_PLANNER_HPP_

#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include "nav2_core/global_planner.hpp"
#include "nav_msgs/msg/path.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_costmap_2d/costmap_2d_ros.hpp"
#include "rclcpp/rclcpp.hpp"

namespace nav2_weighted_astar_planner
{

class WeightedAStarPlanner : public nav2_core::GlobalPlanner
{
public:
  WeightedAStarPlanner() = default;
  ~WeightedAStarPlanner() override = default;

  void configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
    std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;

  void cleanup() override;
  void activate() override;
  void deactivate() override;

  nav_msgs::msg::Path createPlan(
    const geometry_msgs::msg::PoseStamped & start,
    const geometry_msgs::msg::PoseStamped & goal) override;

private:
  rclcpp_lifecycle::LifecycleNode::SharedPtr node_;
  std::string name_;
  std::shared_ptr<tf2_ros::Buffer> tf_;
  nav2_costmap_2d::Costmap2D * costmap_;
  std::string global_frame_;
  double origin_x_, origin_y_, resolution_;
  unsigned int width_, height_;
  size_t map_size_;

  bool weightedAStarShortestPath(
    const int & start_index,
    const int & goal_index,
    const std::vector<int> & costmap_flat,
    std::vector<int> & shortest_path);

  void fromWorldToGrid(float & x, float & y);
  bool inGridMapBounds(const float & x, const float & y);
  size_t gridCellxyToIndex(const float & x, const float & y);
  void fromIndexToGridCellxy(size_t index, int & x, int & y);
  void fromGridToWorld(float & x, float & y);
};

}  // namespace nav2_weighted_astar_planner

#endif  // NAV2_WEIGHTED_ASTAR_PLANNER_HPP_
